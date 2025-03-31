from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar Flask-CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Cargar las credenciales desde la variable de entorno
cred_json = os.environ.get("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(json.loads(cred_json))  # Convertir la cadena JSON en un diccionario
firebase_admin.initialize_app(cred)

app = Flask(__name__)

# Configuración de CORS: Permitir únicamente solicitudes desde Vercel
CORS(app, resources={r"/api/*": {"origins": "https://app-estudio.vercel.app"}})

@app.route('/api/lecciones', methods=['GET'])
def get_lecciones():
    try:
        db = firestore.client()
        lecciones_ref = db.collection('lecciones')  # Consulta la colección 'lecciones'
        lecciones = lecciones_ref.stream()
        data = [{"id": leccion.id, "contenido": leccion.to_dict()} for leccion in lecciones]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clases', methods=['GET'])
def get_clases():
    try:
        db = firestore.client()
        clases_ref = db.collection('Clases')  # Accede a la colección 'Clases' con C mayúscula
        clases = clases_ref.stream()
        data = [{"id": clase.id, "contenido": clase.to_dict()} for clase in clases]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lecciones/<leccion_id>', methods=['GET'])
def get_leccion(leccion_id):
    try:
        db = firestore.client()
        leccion_ref = db.collection('lecciones').document(leccion_id)
        leccion = leccion_ref.get()
        if leccion.exists:
            return jsonify({"contenido": leccion.to_dict()}), 200
        else:
            return jsonify({"error": "Lección no encontrada"}), 404
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
    


# Inicializar Firebase
from firebase_admin import credentials, initialize_app

# Obtener las credenciales desde la variable de entorno
cred_json = os.environ.get("FIREBASE_CREDENTIALS")
if not cred_json:
    raise Exception("Las credenciales de Firebase no están configuradas como variable de entorno.")
cred = credentials.Certificate(json.loads(cred_json))  # Convertir la cadena JSON en un diccionario
initialize_app(cred)


@app.route('/api/libros', methods=['GET'])
def get_libro():
    try:
        # Obtener los parámetros de la solicitud
        grado = request.args.get('grado')
        materia = request.args.get('materia')
        print(f"Parámetros recibidos: grado={grado}, materia={materia}")  # Log para depuración

        # Acceder directamente al documento con el ID especificado
        db = firestore.client()
        libro_ref = db.collection('libros').document('UGnlQLnPrig55tSmgeTu')
        libro = libro_ref.get()

        # Verificar si el documento existe
        if not libro.exists:
            print("Documento no encontrado en Firestore.")
            return jsonify({"error": "Libro no encontrado"}), 404

        # Convertir los datos del documento en un diccionario
        data = libro.to_dict()
        print(f"Datos obtenidos del documento: {data}")  # Log de los datos obtenidos

        # Validar si los parámetros coinciden con los datos del documento
        if data.get('grado') == grado and data.get('materia') == materia:
            print("Parámetros coinciden. Enviando datos del libro.")
            return jsonify(data), 200

        # Si los parámetros no coinciden, devolver error
        print("El libro no coincide con los parámetros proporcionados.")
        return jsonify({"error": "Libro no encontrado"}), 404
    except Exception as e:
        # Manejar cualquier error inesperado y registrarlo
        print(f"Error al ejecutar el endpoint /api/libros: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto proporcionado por Render
    app.run(host='0.0.0.0', port=port, debug=True)
