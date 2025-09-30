from fastapi import FastAPI
from app.routes import mesas, pedidos, cardapio, usuarios

app = FastAPI(title="FlowOrder API", version="1.0")

# Registrar rotas
app.include_router(mesas.router)
app.include_router(pedidos.router)
app.include_router(cardapio.router)
app.include_router(usuarios.router)

@app.get("/")
def root():
    return {"status": "FlowOrder API rodando 🚀"}
