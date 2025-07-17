from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar Flask-CORS
import os
import json
from firebase_admin import credentials, firestore, initialize_app, get_app

# Inicializar Firebase (asegurarse de que solo se inicialice una vez)
try:
    # Comprobar si ya existe una aplicación Firebase inicializada
    firebase_app = get_app()
    print("Firebase ya está inicializado.")
except ValueError:
    # Inicializar Firebase si no está inicializado
    print("Inicializando Firebase...")
    cred_json = os.environ.get("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise Exception("Las credenciales de Firebase no están configuradas como variable de entorno.")
    cred = credentials.Certificate(json.loads(cred_json))  # Convertir la cadena JSON en un diccionario
    initialize_app(cred)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de CORS: Permitir únicamente solicitudes desde Vercel
CORS(app, resources={r"/api/*": {"origins": "https://app-estudio.vercel.app"}})


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

@app.route('/api/lecciones', methods=['GET'])
def get_lecciones():
    try:
        db = firestore.client()
        materia = request.args.get('materia')  # lenguaje o matematicas

        lecciones_ref = db.collection('lecciones')  # 🔧 Debe ser en minúsculas si así está en Firestore
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
