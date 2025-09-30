import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase (precisa do arquivo serviceAccountKey.json na raiz do projeto)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
