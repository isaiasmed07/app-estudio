from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase Admin SDK
cred = credentials.Certificate('firebase/credentials.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route('/api/lecciones', methods=['GET'])
def get_lecciones():
    db = firestore.client()
    lecciones_ref = db.collection('lecciones')
    lecciones = lecciones_ref.stream()
    data = [{"id": leccion.id, "contenido": leccion.to_dict()} for leccion in lecciones]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
