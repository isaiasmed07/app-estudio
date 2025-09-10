from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import requests
import io
import hashlib
import uuid
from vercel_blob import put, list as blob_list

from firebase_admin import credentials, firestore, initialize_app, get_app

import fitz  # PyMuPDF
from ebooklib import epub
from PIL import Image

# ---------- Inicializar Firebase ----------
try:
    firebase_app = get_app()
    print("Firebase ya está inicializado.")
except ValueError:
    print("Inicializando Firebase...")
    cred_json = os.environ.get("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise Exception("Las credenciales de Firebase no están configuradas como variable de entorno.")
    cred = credentials.Certificate(json.loads(cred_json))
    initialize_app(cred)

app = Flask(__name__)
CORS(app)

def url_to_hash(url):
    return hashlib.sha256(url.encode()).hexdigest()

# ---------- CLASES ----------
@app.route('/api/clases', methods=['GET'])
def get_clases():
    try:
        db = firestore.client()
        clases_ref = db.collection('Clases')
        clases = clases_ref.stream()
        data = [{"id": clase.id, "contenido": clase.to_dict()} for clase in clases]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clases/<clase_id>', methods=['GET'])
def get_clase(clase_id):
    try:
        db = firestore.client()
        clase_ref = db.collection('Clases').document(clase_id)
        clase = clase_ref.get()
        if clase.exists:
            return jsonify({"contenido": clase.to_dict()}), 200
        else:
            return jsonify({"error": "Clase no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/listar-videos', methods=['GET'])
def listar_videos():
    """
    Lista los videos de una materia desde Dropbox (nueva ubicación y estructura A).
    Parámetro GET: materia = lenguaje | matematicas
    """
    try:
        materia = request.args.get("materia", "").strip().lower()
        if materia not in ["lenguaje", "matematicas"]:
            return jsonify({"error": "Materia no válida"}), 400

        # Rutas correctas en Dropbox (carpeta Aplicaciones)
        DROPBOX_PATHS = {
            "lenguaje": "/Aplicaciones/plataforma_educativa_castaño/PRIMER GRADO/Clases/Lenguaje/CLASES.json",
            "matematicas": "/Aplicaciones/plataforma_educativa_castaño/PRIMER GRADO/Clases/Matematicas/Matematicas.json"
        }

        file_path = DROPBOX_PATHS[materia]

        # Descargar JSON desde Dropbox
        data = _download_dropbox_json(file_path) or []

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- LECCIONES ----------
@app.route('/api/lecciones', methods=['GET'])
def get_lecciones():
    try:
        db = firestore.client()
        materia = request.args.get('materia')

        lecciones_ref = db.collection('Lecciones')
        lecciones = lecciones_ref.stream()

        data = []
        for leccion in lecciones:
            contenido = leccion.to_dict()
            if materia:
                if contenido.get('materia', '').lower() == materia.lower():
                    data.append({"id": leccion.id, "contenido": contenido})
            else:
                data.append({"id": leccion.id, "contenido": contenido})

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- LIBROS (listado filtrado por grado y opcionalmente materia) ----------
@app.route('/api/libros', methods=['GET'])
def get_libros():
    try:
        grado = request.args.get('grado')
        materia = request.args.get('materia')  # opcional

        if not grado:
            return jsonify({"error": "Falta parámetro 'grado'"}), 400

        db = firestore.client()
        # ⚠️ colección sensible a mayúsculas
        query = db.collection('Libros').where('grado', '==', grado)
        if materia:
            query = query.where('materia', '==', materia.lower())

        docs = query.stream()
        salida = []
        count = 0
        for doc in docs:
            data = doc.to_dict()
            salida.append({
                "id": doc.id,
                "contenido": data
            })
            count += 1

        print(f"[DEBUG] Encontrados {count} libros para grado={grado}, materia={materia}")

        return jsonify(salida), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- SUBIR EPUB DIRECTO ----------
@app.route('/api/subir-epub', methods=['POST'])
def subir_epub():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "Archivo no proporcionado"}), 400

    try:
        filename = file.filename
        file_content = file.read()
        result = put(filename, file_content, options={"allowOverwrite": True})

        return jsonify({
            "message": "Archivo EPUB subido exitosamente.",
            "public_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- SUBIR PDF ----------
@app.route('/api/subir-pdf', methods=['POST'])
@app.route('/api/subir-pdf', methods=['POST'])
def subir_pdf():
    file = request.files.get('file')
    grado = request.form.get('grado')
    materia = request.form.get('materia')

    if not file:
        return jsonify({"error": "Archivo no proporcionado"}), 400

    if file.content_length and file.content_length > 20 * 1024 * 1024:
        return jsonify({"error": "El archivo PDF supera los 20MB"}), 400

    # 👉 Validar grado
    if grado != "1":
        return jsonify({"error": "Función no disponible para este grado. Solo PRIMER GRADO está habilitado."}), 400

    # 👉 Validar materia
    materias_disponibles = ["lenguaje", "matematicas"]
    if materia not in materias_disponibles:
        return jsonify({"error": "Materia no disponible para el grado actual."}), 400

    try:
        filename = file.filename

        # 👉 Definir carpeta de destino
        carpeta = f"PRIMER-GRADO/1-{materia.upper()}/{filename}"

        # 👉 Subir al blob en la carpeta
        file_content = file.read()
        result = put(carpeta, file_content, options={"allowOverwrite": True})

        # 👉 Guardar en firestore tarea pendiente
        db = firestore.client()
        hash_id = url_to_hash(result["url"])
        db.collection('epub_tasks').document(hash_id).set({
            "status": "pending",
            "pdf_url": result["url"],
            "grado": grado,
            "materia": materia
        })

        return jsonify({
            "message": "PDF recibido y almacenado en carpeta correspondiente. Procesamiento en segundo plano.",
            "pdf_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- PROCESAR PDF Y CONVERTIR A EPUB ----------
@app.route('/api/procesar-pdf', methods=['POST'])
def procesar_pdf():
    data = request.get_json()
    pdf_url = data.get('pdf_url')

    if not pdf_url:
        return jsonify({"error": "No se proporcionó la URL del PDF."}), 400

    try:
        # 👉 Extraer nombre del archivo
        filename = pdf_url.split("/")[-1]
        nombre_base = filename.replace(".pdf", "").replace("-", " ").replace("_", " ").strip()
        nombre_base = ' '.join(nombre_base.split())  # Limpieza de espacios

        # 👉 Buscar número de lección si está en el nombre
        import re
        match = re.search(r'leccion\s*(\d+)', nombre_base, re.IGNORECASE)
        if match:
            num_leccion = match.group(1)
            titulo = f"Lección {num_leccion}: {nombre_base.title()}"
        else:
            titulo = nombre_base.title()

        response = requests.get(pdf_url)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo descargar el PDF."}), 400

        pdf_bytes = response.content

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        book = epub.EpubBook()
        book.set_identifier('pdf-to-epub')
        book.set_title(titulo)   # 👉 Título personalizado
        book.set_language('es')

        spine = []
        for idx, page in enumerate(doc):
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            img_filename = f'image_{idx}.jpg'
            epub_image = epub.EpubImage()
            epub_image.file_name = img_filename
            epub_image.media_type = 'image/jpeg'
            epub_image.content = img_data
            book.add_item(epub_image)

            html_content = f'<html><body><img src="{img_filename}" alt="Página {idx+1}" style="width:100%;"/></body></html>'
            c = epub.EpubHtml(title=f'Página {idx+1}', file_name=f'page_{idx+1}.xhtml', content=html_content)
            book.add_item(c)
            spine.append(c)

        book.spine = ['nav'] + spine
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub_bytes = io.BytesIO()
        epub.write_epub(epub_bytes, book)
        epub_bytes.seek(0)

        epub_filename = f'LibroGenerado-{uuid.uuid4()}.epub'
        result = put(epub_filename, epub_bytes.read(), options={"allowOverwrite": True})

        db = firestore.client()
        hash_id = url_to_hash(pdf_url)
        db.collection('epub_tasks').document(hash_id).set({
            'status': 'done',
            'pdf_url': pdf_url,
            'epub_url': result["url"],
            'titulo': titulo
        })

        return jsonify({
            "message": f"EPUB generado exitosamente con título: {titulo}.",
            "epub_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ESTADO EPUB ----------
@app.route('/api/estado-epub', methods=['GET'])
def estado_epub():
    pdf_url = request.args.get('pdf_url')
    if not pdf_url:
        return jsonify({"error": "Falta el parámetro pdf_url"}), 400

    try:
        db = firestore.client()
        hash_id = url_to_hash(pdf_url)
        task_ref = db.collection('epub_tasks').document(hash_id)
        task = task_ref.get()

        if not task.exists:
            return jsonify({"status": "not_found"}), 404

        data = task.to_dict()
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- LISTAR ARCHIVOS ----------
@app.route('/api/listar-archivos', methods=['GET'])
def listar_archivos():
    try:
        blobs = blob_list()
        archivos = [{"url": blob["url"], "size": blob["size"]} for blob in blobs["blobs"]]
        return jsonify({"archivos": archivos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- ELIMINAR ARCHIVO ----------
# ----------------- ADMIN (crear/listar/eliminar libros y lecciones) -----------------
from jose import jwt, JWTError
import requests
import os, json

import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase solo una vez usando variable de entorno
if not firebase_admin._apps:
    firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")
    if not firebase_credentials:
        raise Exception("❌ Falta la variable de entorno FIREBASE_CREDENTIALS")

    cred_dict = json.loads(firebase_credentials)  # convertir string JSON -> dict
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")

def is_professor(email: str) -> bool:
    if not email:
        return False
    return email.strip().lower() in PROFESSOR_EMAILS

def _get_rsa_key(token):
    """Obtiene la clave RSA válida desde JWKS de Auth0 para verificar token."""
    if not AUTH0_DOMAIN:
        return None
    jwks_uri = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_uri, timeout=5).json()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key.get("kty"),
                "kid": key.get("kid"),
                "use": key.get("use"),
                "n": key.get("n"),
                "e": key.get("e")
            }
    return None

def verify_auth0_token(token: str):
    """Verifica un id_token de Auth0 y devuelve el payload (o lanza excepción)."""
    if not token:
        raise Exception("Token ausente")
    rsa_key = _get_rsa_key(token)
    if not rsa_key:
        raise Exception("No se pudo obtener la clave JWKS")
    issuer = f"https://{AUTH0_DOMAIN}/"
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=AUTH0_CLIENT_ID,
        issuer=issuer
    )
    return payload

def get_email_from_request():
    """Extrae email del Authorization Bearer id_token (preferido). 
       Si no hay token, intenta extraer 'email' de query/body."""
    auth = request.headers.get("Authorization", None)
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = verify_auth0_token(token)
            return payload.get("email")
        except Exception as e:
            print("[auth0 verify error]", str(e))
            return None
    email = (request.args.get("email") or (request.json.get("email") if request.is_json else None))
    return email

# Ruta para agregar (crear) libro o lección
@app.route('/api/admin/agregar', methods=['POST'])
def admin_agregar():
    try:
        email = get_email_from_request()
        if not is_professor(email):
            return jsonify({"error": "Acceso restringido. Solo profesores."}), 403

        data = request.get_json(force=True)
        tipo = (data.get("tipo") or "").strip().lower()
        if tipo not in ("libros", "lecciones"):
            return jsonify({"error": "Tipo inválido. 'libros' o 'lecciones'."}), 400

        titulo = (data.get("titulo") or "").strip()
        descripcion = (data.get("descripcion") or "").strip()
        materia = (data.get("materia") or "").strip().lower()
        contenido_html = (data.get("contenido_html") or "").strip()
        grado = (data.get("grado") or "").strip()

        if not titulo or not materia or not contenido_html:
            return jsonify({"error": "Faltan campos obligatorios: titulo, materia, contenido_html"}), 400

        if tipo == "libros":
            if not grado:
                return jsonify({"error": "Para 'libros' es obligatorio el campo 'grado'."}), 400
            doc_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "grado": grado,
                "materia": materia,
                "contenido_html": contenido_html
            }
            doc_ref = db.collection("Libros").document()
            doc_ref.set(doc_data)
            return jsonify({"message": "Libro creado", "id": doc_ref.id}), 200

        else:  # lecciones
            doc_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "materia": materia,
                "contenido_html": contenido_html
            }
            doc_ref = db.collection("Lecciones").document()
            doc_ref.set(doc_data)
            return jsonify({"message": "Lección creada", "id": doc_ref.id}), 200

    except Exception as e:
        print("[admin_agregar] Exception:", str(e))
        return jsonify({"error": str(e)}), 500

# Ruta para listar (devuelve id + titulo)
@app.route('/api/admin/listar', methods=['GET'])
def admin_listar():
    try:
        email = get_email_from_request()
        if not is_professor(email):
            return jsonify({"error": "Acceso restringido. Solo profesores."}), 403

        tipo = (request.args.get("tipo") or "libros").strip().lower()
        if tipo not in ("libros", "lecciones"):
            return jsonify({"error": "Tipo inválido. 'libros' o 'lecciones'."}), 400

        col_name = "Libros" if tipo == "libros" else "Lecciones"
        docs = db.collection(col_name).stream()

        salida = []
        for d in docs:
            contenido = d.to_dict() or {}
            salida.append({
                "id": d.id,
                "titulo": contenido.get("titulo", "(sin titulo)"),
                "metadata": contenido
            })

        return jsonify(salida), 200

    except Exception as e:
        print("[admin_listar] Exception:", str(e))
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar por id
@app.route('/api/admin/eliminar', methods=['DELETE'])
def admin_eliminar():
    try:
        email = get_email_from_request()
        if not is_professor(email):
            return jsonify({"error": "Acceso restringido. Solo profesores."}), 403

        data = request.get_json(force=True)
        tipo = (data.get("tipo") or "").strip().lower()
        doc_id = (data.get("id") or "").strip()
        if tipo not in ("libros", "lecciones") or not doc_id:
            return jsonify({"error": "Faltan campos: tipo (libros|lecciones), id"}), 400

        col_name = "Libros" if tipo == "libros" else "Lecciones"
        doc_ref = db.collection(col_name).document(doc_id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Documento no encontrado"}), 404

        doc_ref.delete()
        return jsonify({"message": f"Documento {doc_id} eliminado de {col_name}"}), 200

    except Exception as e:
        print("[admin_eliminar] Exception:", str(e))
        return jsonify({"error": str(e)}), 500




# ---------- LISTAR DOCUMENTOS ----------
@app.route('/admin/listar', methods=['GET'])
def listar_documentos():
    coleccion = request.args.get("coleccion")
    if not coleccion:
        return jsonify({"error": "Falta el parámetro 'coleccion'"}), 400

    try:
        docs = db.collection(coleccion).stream()
        resultados = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id  # incluir el ID del documento
            resultados.append(data)

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ---------- AGREGAR VIDEO A JSON EN DROPBOX ----------
from flask import request, jsonify
from flask_cors import CORS
import requests
import json
import os

# ===================================
# Configuración global de CORS
# ===================================
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://app-estudio.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.before_request
def handle_preflight():
    """Maneja las solicitudes OPTIONS para evitar problemas de CORS"""
    if request.method == "OPTIONS":
        return '', 200

# ===================================
# Configuración para Refresh Token de Dropbox
# ===================================
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

# Diccionario con rutas según materia (Ruta B en Aplicaciones)
DROPBOX_PATHS = {
    "lenguaje": "/Aplicaciones/plataforma_educativa_castaño/PRIMER GRADO/Clases/Lenguaje/CLASES.json",
    "matematicas": "/Aplicaciones/plataforma_educativa_castaño/PRIMER GRADO/Clases/Matematicas/Matematicas.json"
}

def get_dropbox_access_token():
    """Obtiene un Access Token válido usando el Refresh Token."""
    if not DROPBOX_REFRESH_TOKEN:
        raise Exception("Falta la variable de entorno DROPBOX_REFRESH_TOKEN")
    
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN
    }
    resp = requests.post(url, data=data, auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET), timeout=10)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        raise Exception(f"Error al refrescar token: {resp.text}")

def _download_dropbox_json(file_path):
    """Descarga y parsea el JSON desde Dropbox."""
    access_token = get_dropbox_access_token()
    url = "https://content.dropboxapi.com/2/files/download"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps({"path": file_path})
    }
    resp = requests.post(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        try:
            return json.loads(resp.content.decode("utf-8"))
        except Exception:
            return []
    elif resp.status_code == 409:  # archivo no existe
        return []
    else:
        raise Exception(f"Error Dropbox download: {resp.status_code} {resp.text}")

def _upload_dropbox_json(file_path, data):
    """Sube el JSON a Dropbox, sobrescribiendo."""
    access_token = get_dropbox_access_token()
    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": file_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": True
        })
    }
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    resp = requests.post(url, headers=headers, data=payload, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Error Dropbox upload: {resp.status_code} {resp.text}")
    return True

# ===================================
# Ruta para agregar video
# ===================================
@app.route('/api/agregar-video', methods=['POST'])
def agregar_video():
    """
    Añade un video (titulo, url, materia) al JSON en Dropbox.
    Materias válidas: lenguaje, matematicas.
    """
    try:
        body = request.get_json(silent=True) or request.form.to_dict()

        titulo = (body.get("titulo") or "").strip()
        url_video = (body.get("url") or "").strip()
        materia = (body.get("materia") or "").strip().lower()
        publico = (body.get("publico") or "niños").strip().lower()

        if not titulo or not url_video or not materia:
            return jsonify({"error": "Faltan campos: titulo, url, materia"}), 400

        allowed = ["lenguaje", "matematicas"]
        if materia not in allowed:
            return jsonify({"error": f"Materia no válida. Opciones: {allowed}"}), 400

        if not ("youtube.com" in url_video or "youtu.be" in url_video):
            return jsonify({"error": "La URL no parece de YouTube"}), 400

        # Obtener ruta de Dropbox según materia
        file_path = DROPBOX_PATHS[materia]

        # Descargar datos actuales
        data = _download_dropbox_json(file_path) or []

        # Agregar nuevo video con estructura tipo Ruta A
        nuevo = {
            "titulo": titulo,
            "url": url_video,
            "publico": publico
        }
        data.append(nuevo)

        # Subir archivo actualizado
        _upload_dropbox_json(file_path, data)

        return jsonify({"message": "Video agregado correctamente", "item": nuevo}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ---------- ROLES (Lista blanca de profesores) ----------
# Cargar emails de profesores desde variable de entorno (Render)
PROFESSOR_EMAILS = {
    e.strip().lower() for e in (os.getenv("PROFESSOR_EMAILS", "").split(","))
    if e.strip()
}

@app.route('/api/rol', methods=['GET', 'OPTIONS'])
def obtener_rol():
    """Devuelve el rol del usuario según lista blanca de profesores"""
    if request.method == 'OPTIONS':
        return '', 200  # Preflight CORS

    email = (request.args.get('email') or "").strip().lower()
    if not email:
        return jsonify({"error": "Falta el parámetro 'email'"}), 400

    es_profe = email in PROFESSOR_EMAILS
    return jsonify({"rol": "profesor" if es_profe else "alumno"}), 200



# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
