from fastapi import APIRouter
from app.services.firebase import db

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.get("/{mesa_id}")
def listar_pedidos(mesa_id: str):
    pedidos = db.collection("pedidos").where("mesa_id", "==", mesa_id).stream()
    return {"pedidos": [{**p.to_dict(), "id": p.id} for p in pedidos]}

@router.post("/")
def criar_pedido(pedido: dict):
    doc_ref = db.collection("pedidos").add(pedido)
    return {"message": "Pedido criado", "id": doc_ref[1].id}
