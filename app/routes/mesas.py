from fastapi import APIRouter
from app.services.firebase import db

router = APIRouter(prefix="/mesas", tags=["Mesas"])

@router.get("/")
def listar_mesas():
    mesas_ref = db.collection("mesas").stream()
    mesas = [{**m.to_dict(), "id": m.id} for m in mesas_ref]
    return {"mesas": mesas}

@router.post("/")
def criar_mesa(mesa: dict):
    doc_ref = db.collection("mesas").add(mesa)
    return {"message": "Mesa criada", "id": doc_ref[1].id}
