from pydantic import BaseModel, validator
from typing import Optional, Dict, Any

class ConfiguracaoBase(BaseModel):
    chave: str

class ConfiguracaoTexto(ConfiguracaoBase):
    valor: Optional[str] = None

class ConfiguracaoJSON(ConfiguracaoBase):
    valor_json: Optional[Dict[str, Any]] = None

    @validator('valor_json', pre=True)
    def parse_json(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('JSON inválido')
        return v

class Configuracao(ConfiguracaoBase):
    id: int
    valor: Optional[str] = None
    valor_json: Optional[Dict[str, Any]] = None
