from pydantic import BaseModel
from typing import List, Optional

class CabecalhoPallet(BaseModel):
    tipo_de_caixa: int
    tex_tipoCaixa: str

    des_produto: int
    tex_descProduto: str

    cliente: int
    tex_cliente: str

    tipo_de_etiqueta: int
    tex_tipoEtiqueta: str

    local_de_estoque: int
    tex_localEstoque: str

    processo_interno: int


class ItemPallet(BaseModel):
    esteira: int
    tex_esteira: str

    latada: str
    q_caixas: int
    cor: str
    calibre: int
    brix: int

    observacoes: Optional[str] = None


class RegistroPallet(BaseModel):
    cabecalho: CabecalhoPallet
    itens: List[ItemPallet]