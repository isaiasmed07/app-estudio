from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar el archivo de credenciales desde la ruta absoluta
cred = credentials.Certificate(r'C:\app-estudio-clean\firebase\app-escuela-c3504-firebase-adminsdk-fbsvc-27b9fd6d46.json')
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
    app.run(debug=True)
