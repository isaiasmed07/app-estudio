from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar Flask-CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Cargar las credenciales desde la variable de entorno
cred_json = os.environ.get("FIREBASE_CREDENTIALS")
if cred_json:  # Validar que las credenciales existan
    cred = credentials.Certificate(json.loads(cred_json))  # Convertir la cadena JSON en un diccionario
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("Las credenciales de Firebase no están configuradas correctamente.")

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto proporcionado por Render
    app.run(host='0.0.0.0', port=port, debug=True)
