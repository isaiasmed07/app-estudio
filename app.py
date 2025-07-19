from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import json
import requests
import io
from vercel_blob import put

from firebase_admin import credentials, firestore, initialize_app, get_app

from pdf2image import convert_from_bytes
from ebooklib import epub
from PIL import Image

# Inicializar Firebase
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
        print(f"Parámetros recibidos: grado={grado}, materia={materia}")

        db = firestore.client()
        libro_ref = db.collection('libros').document('UGnlQLnPrig55tSmgeTu')
        libro = libro_ref.get()

        if not libro.exists:
            print("Documento no encontrado en Firestore.")
            return jsonify({"error": "Libro no encontrado"}), 404

        data = libro.to_dict()
        print(f"Datos obtenidos del documento: {data}")

        if data.get('grado') == grado and data.get('materia') == materia:
            print("Parámetros coinciden. Enviando datos del libro.")
            return jsonify(data), 200

        print("El libro no coincide con los parámetros proporcionados.")
        return jsonify({"error": "Libro no encontrado"}), 404

    except Exception as e:
        print(f"Error al ejecutar el endpoint /api/libros: {e}")
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

        result = put(filename, file_content)

        return jsonify({
            "message": "Archivo EPUB subido exitosamente.",
            "public_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- CONVERTIR PDF A EPUB ----------
@app.route('/api/convertir-pdf', methods=['POST'])
def convertir_pdf():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "Archivo no proporcionado"}), 400

    if len(file.read()) > 20 * 1024 * 1024:  # 20MB
        return jsonify({"error": "El archivo PDF supera los 20MB"}), 400

    file.seek(0)  # Regresar al inicio del archivo después de .read()

    try:
        images = convert_from_bytes(file.read())

        # Crear EPUB
        book = epub.EpubBook()
        book.set_identifier("pdf-convertido")
        book.set_title("PDF Convertido a EPUB")
        book.set_language("es")

        spine = ['nav']
        toc = []

        for i, image in enumerate(images):
            img_io = io.BytesIO()
            image.save(img_io, format='PNG')
            img_io.seek(0)
            img_data = img_io.read()

            img_name = f"imagen_{i}.png"
            epub_img = epub.EpubImage()
            epub_img.file_name = img_name
            epub_img.media_type = "image/png"
            epub_img.content = img_data
            book.add_item(epub_img)

            html = f'<html><body><img src="{img_name}" style="width:100%;"/></body></html>'
            chapter = epub.EpubHtml(title=f'Página {i+1}', file_name=f'page_{i+1}.xhtml', content=html)
            book.add_item(chapter)
            spine.append(chapter)
            toc.append(epub.Link(f'page_{i+1}.xhtml', f'Página {i+1}', f'page_{i+1}'))

        book.toc = tuple(toc)
        book.spine = spine

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub_buffer = io.BytesIO()
        epub.write_epub(epub_buffer, book)
        epub_buffer.seek(0)

        filename = file.filename.replace(".pdf", ".epub")
        result = put(filename, epub_buffer.read())

        return jsonify({
            "message": "PDF convertido y subido exitosamente.",
            "public_url": result["url"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
