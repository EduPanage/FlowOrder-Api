from fastapi import APIRouter
from app.services.firebase import db

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.get("/")
def listar_usuarios():
    usuarios = db.collection("usuarios").stream()
    return {"usuarios": [{**u.to_dict(), "id": u.id} for u in usuarios]}

@router.post("/")
def criar_usuario(usuario: dict):
    doc_ref = db.collection("usuarios").add(usuario)
    return {"message": "Usuário criado", "id": doc_ref[1].id}
