from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from firebase_admin import credentials, firestore, initialize_app, get_app

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

# CORS
CORS(app, resources={r"/api/*": {"origins": "https://app-estudio.vercel.app"}})

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
        materia = request.args.get('materia')  # lenguaje o matematicas

        # Corregido: nombre de la colección con mayúscula
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

# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
