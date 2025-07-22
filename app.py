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
@app.route('/api/libros', methods=['GET'])
def get_libro():
    try:
        grado = request.args.get('grado')
        materia = request.args.get('materia')
        db = firestore.client()
        libro_ref = db.collection('libros').document('UGnlQLnPrig55tSmgeTu')
        libro = libro_ref.get()

        if not libro.exists:
            return jsonify({"error": "Libro no encontrado"}), 404

        data = libro.to_dict()
        if data.get('grado') == grado and data.get('materia') == materia:
            return jsonify(data), 200

        return jsonify({"error": "Libro no encontrado"}), 404

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
def subir_pdf():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "Archivo no proporcionado"}), 400

    if file.content_length and file.content_length > 20 * 1024 * 1024:
        return jsonify({"error": "El archivo PDF supera los 20MB"}), 400

    try:
        filename = file.filename
        file_content = file.read()
        result = put(filename, file_content, options={"allowOverwrite": True})

        db = firestore.client()
        hash_id = url_to_hash(result["url"])
        db.collection('epub_tasks').document(hash_id).set({
            "status": "pending",
            "pdf_url": result["url"]
        })

        return jsonify({
            "message": "PDF recibido. Procesamiento en segundo plano.",
            "pdf_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- PROCESAR PDF Y CONVERTIR A EPUB ----------
@app.route('/api/procesar-pdf', methods=['POST'])
def procesar_pdf():
    data = request.get_json()
    pdf_url = data.get('pdf_url')
    titulo = data.get('titulo', 'Libro Generado')  # Puedes pasar el nombre de la lección si lo deseas

    if not pdf_url:
        return jsonify({"error": "No se proporcionó la URL del PDF."}), 400

    try:
        response = requests.get(pdf_url)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo descargar el PDF."}), 400

        pdf_bytes = response.content

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        book = epub.EpubBook()
        book.set_identifier('pdf-to-epub')
        book.set_title(titulo)  # 👉 Aquí puedes pasar el título dinámico si quieres
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

            # 👉 Si es la primera página, usarla como portada
            if idx == 0:
                book.set_cover(img_filename, img_data)

        book.spine = ['nav'] + spine  # Mantiene TOC sin página extra
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
            "message": "EPUB generado exitosamente.",
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


# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
