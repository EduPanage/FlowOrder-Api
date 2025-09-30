from fastapi import APIRouter
from app.services.firebase import db

router = APIRouter(prefix="/cardapio", tags=["Cardápio"])

@router.get("/")
def listar_itens():
    itens = db.collection("cardapio").stream()
    return {"cardapio": [{**i.to_dict(), "id": i.id} for i in itens]}

@router.post("/")
def adicionar_item(item: dict):
    doc_ref = db.collection("cardapio").add(item)
    return {"message": "Item adicionado", "id": doc_ref[1].id}
