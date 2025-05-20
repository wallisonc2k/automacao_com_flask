from api import db
from api.models.config_model import ConfiguracaoModel
from typing import Dict, Any, List, Optional
import json

def listar_configuracoes():
    return ConfiguracaoModel.query.all()

def obter_configuracao_texto(chave: str) -> Optional[str]:
    config = ConfiguracaoModel.query.filter_by(chave=chave).first()
    return config.valor if config else None

def obter_configuracao_json(chave: str) -> Optional[Dict[str, Any]]:
    config = ConfiguracaoModel.query.filter_by(chave=chave).first()
    return config.valor_json if config else None

def salvar_configuracao_texto(chave: str, valor: str) -> ConfiguracaoModel:
    config = ConfiguracaoModel.query.filter_by(chave=chave).first()
    
    if config:
        config.valor = valor
    else:
        config = ConfiguracaoModel(chave=chave, valor=valor)
        db.session.add(config)
    
    db.session.commit()
    db.session.refresh(config)
    return config

def salvar_configuracao_json(chave: str, valor_json: Dict[str, Any]) -> ConfiguracaoModel:
    config = ConfiguracaoModel.query.filter_by(chave=chave).first()
    
    if config:
        config.valor_json = valor_json
    else:
        config = ConfiguracaoModel(chave=chave, valor_json=valor_json)
        db.session.add(config)
    
    db.session.commit()
    db.session.refresh(config)
    return config

def deletar_configuracao(chave: str) -> bool:
    config = ConfiguracaoModel.query.filter_by(chave=chave).first()
    
    if config:
        db.session.delete(config)
        db.session.commit()
        return True
    
    return False

def obter_todas_configuracoes() -> List[ConfiguracaoModel]:
    return ConfiguracaoModel.query.all()
