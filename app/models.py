from pydantic import BaseModel, Field
from typing import List, Optional

class Cardapio(BaseModel):
    nome: str = Field(..., min_length=1)
    descricao: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    categoria: str = Field(default="Outros")
    ativo: bool = Field(default=True)

class Mesa(BaseModel):
    numero: int = Field(..., gt=0)
    nome: str = Field(default="")

class ItemCardapio(BaseModel):
    uid: Optional[str] = None
    nome: str
    preco: float = Field(..., gt=0)
    categoria: str
    quantidade: int = Field(default=1, ge=1)
    observacao: Optional[str] = None

class MesaPedido(BaseModel):
    uid: Optional[str] = None
    numero: int
    nome: str = ""

class Pedido(BaseModel):
    mesa: MesaPedido 
    itens: List[ItemCardapio] = Field(..., min_items=1)
    statusAtual: str = Field(default="Aberto")
    observacao: Optional[str] = None