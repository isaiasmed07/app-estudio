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

# ---------- LIBROS ----------
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

@app.route('/api/eliminar-archivo', methods=['POST'])
def eliminar_archivo():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400

    try:
        filename = url.split("/")[-1]

        vercel_token = os.environ.get("VERCEL_BLOB_TOKEN")  # 👉 Crea esta variable en Render dashboard

        if not vercel_token:
            return jsonify({"error": "Falta VERCEL_BLOB_TOKEN en variables de entorno"}), 500

        delete_url = f"https://blob.vercel-storage.com/{filename}"
        headers = {
            "Authorization": f"Bearer {vercel_token}"
        }

        response = requests.delete(delete_url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": f"No se pudo eliminar el archivo: {response.text}"}), 500

        return jsonify({"message": f"Archivo {filename} eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ---------- AGREGAR VIDEO A JSON EN DROPBOX ----------
from flask_cors import cross_origin
import requests
import json
from flask import request, jsonify

DROPBOX_ACCESS_TOKEN = "sl.u.AF6J3-ChtJ2ieVvVRcP1GSAzzZvh3Wix6gnUsowfGJK9_TYY1EB-gcHrpClpjikdQv-NQjAG3XEZIzoSIuPXjB1O_LFyzCS3uLy86NdyndMdnPrUWU2UdkSJuBlNSU-dEeSJWJTAEsxkMCsaH80xnXxXTtIUA9_bxoVSbEfQ1QtSv_WVgoCs6TjwmSFu1LYz2zRNPB4sKhlu0R98TRD-Qb8vB3lOCypMQErFc0thTfB3liMmIS460IgnUM4FVirJ5RlJvC2XKT-_9SzTXvbc4rs6SYt7uGkgb3MifdyrRT5GYJOzARK-T4oPl4HM8YgAI0Td3A1hMrBAebQQYMQWTdQ8GJ1lALKdmBA4Yey-fbraH9bNJSyNMpcxcr_9I6-d3socclM91mrSFKMFf-kR50OomezVA4cNRUa1U_vqROJ-JTD-PjgXDmGrPGFJ68tcTB7WYY9bGJ2rFzwSRJg63ZzSxwRR1zalqh25Vyz1GXc-VbpwTPi2rQRsLdJc7yEpciXPE9AKPFhvs6if6flZVt8xJ_A71ji2E7Pq1nIXu6NlXCwnjovhqOzvprs9RWR5kYZjrxWanQmFC4Zco8zBOqhbZDv5Tcst0Y0pObU6Gdp1oZAP4kBb9_-ElA0dOnCe_A1iFgYX9AcnlUGS1CleOJhNTvxK36fPuwsy9oBdDZWWsLway36cp1a6On-21fd2a9k7jfH7eu-mjBgFJhlCt7SWT7_2r_dY7bTTaNdf7CxoNWRRR86RYqeEmjUGq_UUgfj4wN24VoU2a5d2K9FcU9IFf1CmZHlxRZwILLH4gi-K-xx-DALYgfYRNC5jozSeXh8CJ69kobNdPgaoxCxFm3S6Z_gncRu6BY5HQx81JVbAjnLAsSaDE55x2zFHYJu2-w4Ttr9HM4qIc-rsCtYSL10exPnR6Dfb2oMmCBJ1qEbznpMy1UzsMQGAbHEiqkxvZODf2CuX-9hfXwT8LRtW2Vv7ixv3pVvOTBP83ePYxquYe_S5_m46OPY0v95sx0dCuDyPTkbxrxh_OqERho0Kumh_MrUwg0Sd42bs8Q4Ux4ePLCJ5YYb5v93GFNq7d0EHnN1p0P7cL2kganoIHllsUNSRSGJWj4zONDHiAjMBc73aF7dwbSfgixFhdAOrf183W6ndy8z4ZXP0je8dsQyIKw5EajX0U2chGjB_B8-d_MCeyDBktjVFMvtMRrvsHc9uqlRYsW3jfkOQUF1E62k8GLdjzj48zfpINnqVqvKc5NsgbH_QZ3l8fuaE0Rp9NmmUDAtfhb4VyCa7zfFnSAwxI1chc6dDiIC79ZcSS3HI9wdzcAdqU3QG68FhL3QQ-wPMnd36cQXCNXLtO-ZpmmT4BP_dDa5ot-pyUKxmBQDQoJ_U__0Q318lSHlRUBq0e4PmrZVf-jpgBY5mCLC-p0li_HFI"
DROPBOX_FILE_PATH = "/clases.json"  # Ruta del archivo JSON en Dropbox


def _download_dropbox_json():
    """Descarga y parsea el JSON desde Dropbox."""
    url = "https://content.dropboxapi.com/2/files/download"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Dropbox-API-Arg": json.dumps({"path": DROPBOX_FILE_PATH})
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


def _upload_dropbox_json(data):
    """Sube el JSON a Dropbox, sobrescribiendo."""
    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": DROPBOX_FILE_PATH,
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


@app.route('/api/agregar-video', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins="https://app-estudio.vercel.app",  # tu dominio real del frontend
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)
def agregar_video():
    """
    Añade un video (titulo, url, materia) al JSON en Dropbox.
    Materias válidas: lenguaje, matematicas.
    """
    if request.method == "OPTIONS":
        # Respuesta para preflight
        return jsonify({"status": "OK"}), 200

    try:
        body = request.get_json(silent=True) or request.form.to_dict()

        titulo = (body.get("titulo") or "").strip()
        url_video = (body.get("url") or "").strip()
        materia = (body.get("materia") or "").strip().lower()

        if not titulo or not url_video or not materia:
            return jsonify({"error": "Faltan campos: titulo, url, materia"}), 400

        allowed = ["lenguaje", "matematicas"]
        if materia not in allowed:
            return jsonify({"error": f"Materia no válida. Opciones: {allowed}"}), 400

        if not ("youtube.com" in url_video or "youtu.be" in url_video):
            return jsonify({"error": "La URL no parece de YouTube"}), 400

        data = _download_dropbox_json() or []
        nuevo = {
            "titulo": titulo,
            "url": url_video,
            "materia": materia
        }
        data.append(nuevo)

        _upload_dropbox_json(data)

        return jsonify({"message": "Video agregado correctamente", "item": nuevo}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
