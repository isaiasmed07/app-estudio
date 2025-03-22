from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Cargar las credenciales desde la variable de entorno
cred_json = os.environ.get("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(json.loads(cred_json))  # Convertir la cadena JSON en un diccionario
firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route('/api/lecciones', methods=['GET'])
def get_lecciones():
    db = firestore.client()
    lecciones_ref = db.collection('lecciones')  # Consulta la colección 'lecciones'
    lecciones = lecciones_ref.stream()
    data = [{"id": leccion.id, "contenido": leccion.to_dict()} for leccion in lecciones]
    return jsonify(data)

@app.route('/api/Lecciones', methods=['GET'])
def get_Lecciones():
    db = firestore.client()
    Lecciones_ref = db.collection('Lecciones')  # Consulta la colección 'Lecciones'
    Lecciones = Lecciones_ref.stream()
    data = [{"id": leccion.id, "contenido": leccion.to_dict()} for leccion in Lecciones]
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto proporcionado por Render
    app.run(host='0.0.0.0', port=port, debug=True)
