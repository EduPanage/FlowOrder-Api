from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.firebase import db
from app.models import Cardapio, Mesa, Pedido
from datetime import datetime
from typing import Optional

app = FastAPI(title="FlowOrder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CARDÁPIO =====
@app.get("/cardapio")
def listar_cardapio(gerente_uid: Optional[str] = None, categoria: Optional[str] = None):
    """Lista itens do cardápio"""
    query = db.collection("Cardapios")
    
    if gerente_uid:
        query = query.where("gerenteUid", "==", gerente_uid)
    if categoria:
        query = query.where("categoria", "==", categoria)
    
    docs = query.stream()
    return [{"uid": d.id, **d.to_dict()} for d in docs]

@app.post("/cardapio")
def adicionar_cardapio(item: Cardapio, gerente_uid: str = Query(...)):
    """Adiciona item ao cardápio"""
    item_dict = item.model_dump()
    item_dict.update({
        "gerenteUid": gerente_uid,
        "criadoEm": datetime.now(),
        "ativo": True
    })
    
    _, doc_ref = db.collection("Cardapios").add(item_dict)
    doc_ref.update({"uid": doc_ref.id}) 
    
    return {"uid": doc_ref.id, **item_dict}

@app.put("/cardapio/{item_id}")
def atualizar_cardapio(item_id: str, item: Cardapio):
    """Atualiza item do cardápio"""
    doc_ref = db.collection("Cardapios").document(item_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(404, "Item não encontrado")
    
    doc_ref.update({
        **item.model_dump(),
        "atualizadoEm": datetime.now()
    })
    
    return {"message": "Item atualizado", "uid": item_id}

@app.delete("/cardapio/{item_id}")
def deletar_cardapio(item_id: str):
    """Deleta item do cardápio"""
    doc_ref = db.collection("Cardapios").document(item_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(404, "Item não encontrado")
    
    doc_ref.delete()
    return {"message": "Item deletado"}

# ===== MESAS =====
@app.get("/mesas")
def listar_mesas(gerente_uid: Optional[str] = None):
    """Lista mesas"""
    query = db.collection("Mesas")
    
    if gerente_uid:
        query = query.where("gerenteUid", "==", gerente_uid)
    
    query = query.order_by("numero")
    docs = query.stream()
    
    return [{"uid": d.id, **d.to_dict()} for d in docs]

@app.post("/mesas")
def criar_mesa(mesa: Mesa, gerente_uid: str = Query(...)):
    """Cria mesa"""
    # Verificar número duplicado
    existing = db.collection("Mesas")\
        .where("gerenteUid", "==", gerente_uid)\
        .where("numero", "==", mesa.numero)\
        .limit(1)\
        .stream()
    
    if len(list(existing)) > 0:
        raise HTTPException(400, "Já existe mesa com este número")
    
    mesa_dict = mesa.model_dump()
    
    # Gerar nome padrão se vazio
    if not mesa_dict["nome"]:
        mesa_dict["nome"] = f"Mesa {mesa_dict['numero']}"
    
    mesa_dict.update({
        "gerenteUid": gerente_uid,
        "criadoEm": datetime.now()
    })
    
    _, doc_ref = db.collection("Mesas").add(mesa_dict)
    doc_ref.update({"uid": doc_ref.id})
    
    return {"uid": doc_ref.id, **mesa_dict}

@app.put("/mesas/{mesa_id}")
def atualizar_mesa(mesa_id: str, mesa: Mesa):
    """Atualiza mesa"""
    doc_ref = db.collection("Mesas").document(mesa_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(404, "Mesa não encontrada")
    
    doc_ref.update({
        **mesa.model_dump(),
        "atualizadoEm": datetime.now()
    })
    
    return {"message": "Mesa atualizada", "uid": mesa_id}

@app.delete("/mesas/{mesa_id}")
def deletar_mesa(mesa_id: str):
    """Deleta mesa"""
    doc_ref = db.collection("Mesas").document(mesa_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(404, "Mesa não encontrada")
    
    doc_ref.delete()
    return {"message": "Mesa deletada"}

# ===== PEDIDOS =====
@app.get("/pedidos")
def listar_pedidos(
    gerente_uid: Optional[str] = None,
    mesa_numero: Optional[int] = None,
    status: Optional[str] = None
):
    """Lista pedidos"""
    query = db.collection("Pedidos")
    
    if gerente_uid:
        query = query.where("gerenteUid", "==", gerente_uid)
    if status:
        query = query.where("statusAtual", "==", status)
    
    query = query.order_by("horario", direction="DESCENDING")
    docs = query.stream()
    
    result = []
    for d in docs:
        pedido = d.to_dict()
        
        # Filtro local por mesa (pois é objeto)
        if mesa_numero and pedido.get("mesa", {}).get("numero") != mesa_numero:
            continue
        
        result.append({"uid": d.id, **pedido})
    
    return result

@app.post("/pedidos")
def criar_pedido(pedido: Pedido, gerente_uid: str = Query(...)):
    """Cria pedido"""
    pedido_dict = pedido.model_dump()
    pedido_dict.update({
        "gerenteUid": gerente_uid,
        "horario": datetime.now(),
        "pago": False
    })
    
    _, doc_ref = db.collection("Pedidos").add(pedido_dict)
    doc_ref.update({"uid": doc_ref.id})
    
    return {"uid": doc_ref.id, **pedido_dict}

@app.patch("/pedidos/{pedido_id}/status")
def atualizar_status(pedido_id: str, status: str = Query(...)):
    """Atualiza status do pedido"""
    doc_ref = db.collection("Pedidos").document(pedido_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(404, "Pedido não encontrado")
    
    # Validar status
    status_validos = ["Aberto", "Em Preparo", "Pronto", "Entregue", "Cancelado"]
    if status not in status_validos:
        raise HTTPException(400, f"Status inválido. Use: {', '.join(status_validos)}")
    
    doc_ref.update({"statusAtual": status})
    return {"message": f"Status atualizado para '{status}'"}

@app.patch("/pedidos/{pedido_id}/pagar")
def processar_pagamento(
    pedido_id: str,
    metodo_pagamento: str = Query(...),
    valor_pago: float = Query(..., gt=0),
    desconto: float = Query(0, ge=0),
    troco: float = Query(0, ge=0)
):
    """Processa pagamento"""
    doc_ref = db.collection("Pedidos").document(pedido_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(404, "Pedido não encontrado")
    
    if doc.to_dict().get("pago"):
        raise HTTPException(400, "Pedido já foi pago")
    
    # Atualizar pedido
    doc_ref.update({
        "pago": True,
        "dataPagamento": datetime.now(),
        "statusAtual": "Entregue"
    })
    
    # Registrar pagamento em subcoleção
    doc_ref.collection("pagamentos").add({
        "metodoPagamento": metodo_pagamento,
        "valorPago": valor_pago,
        "desconto": desconto,
        "troco": troco,
        "dataPagamento": datetime.now(),
        "processadoPor": "api"
    })
    
    return {"message": "Pagamento processado", "pedido_id": pedido_id}

@app.get("/")
def root():
    return {
        "status": "FlowOrder API ativa 🚀",
        "endpoints": {
            "cardapio": "/cardapio",
            "mesas": "/mesas",
            "pedidos": "/pedidos"
        },
        "docs": "/docs"
    }