from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
GERENTE_UID = "test_gerente_123"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_adicionar_e_listar_cardapio():
    # Adicionar
    response = client.post(
        f"/cardapio?gerente_uid={GERENTE_UID}",
        json={
            "nome": "Pizza Test",
            "descricao": "Pizza de teste",
            "preco": 45.90,
            "categoria": "Prato"
        }
    )
    assert response.status_code == 200
    item_id = response.json()["uid"]
    
    # Listar
    response = client.get(f"/cardapio?gerente_uid={GERENTE_UID}")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_criar_e_listar_mesa():
    # Criar
    response = client.post(
        f"/mesas?gerente_uid={GERENTE_UID}",
        json={"numero": 99, "nome": "Mesa Test"}
    )
    assert response.status_code == 200
    mesa_id = response.json()["uid"]
    
    # Listar
    response = client.get(f"/mesas?gerente_uid={GERENTE_UID}")
    assert response.status_code == 200

def test_criar_pedido_completo():
    # Criar pedido com estrutura completa
    response = client.post(
        f"/pedidos?gerente_uid={GERENTE_UID}",
        json={
            "mesa": {
                "numero": 5,
                "nome": "Mesa 5"
            },
            "itens": [
                {
                    "nome": "Hambúrguer",
                    "preco": 25.00,
                    "categoria": "Lanche",
                    "quantidade": 2,
                    "observacao": "Sem cebola"
                }
            ],
            "statusAtual": "Aberto",
            "observacao": "Cliente com pressa"
        }
    )
    assert response.status_code == 200
    pedido = response.json()
    assert "uid" in pedido
    assert pedido["mesa"]["numero"] == 5
    assert len(pedido["itens"]) == 1

def test_atualizar_status_pedido():
    # Criar pedido primeiro
    response = client.post(
        f"/pedidos?gerente_uid={GERENTE_UID}",
        json={
            "mesa": {"numero": 10, "nome": "Mesa 10"},
            "itens": [{"nome": "Café", "preco": 5.0, "categoria": "Bebida", "quantidade": 1}],
            "statusAtual": "Aberto"
        }
    )
    pedido_id = response.json()["uid"]
    
    # Atualizar status
    response = client.patch(f"/pedidos/{pedido_id}/status?status=Pronto")
    assert response.status_code == 200