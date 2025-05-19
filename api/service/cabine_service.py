from api import db
from api.models.cabine_model import CabineModel
from datetime import datetime

def cadastrar_cabine(cabine: CabineModel):
    cabine_bd = CabineModel(
        variedades=cabine.variedades,
        classificacao=cabine.classificacao,
        peso=cabine.peso,
        total_etiquetas=cabine.total_etiquetas,
        modelo_etiquetas=cabine.modelo_etiquetas,
        cabines=cabine.cabines,
        data_registro=cabine.data_registro,
        data_impressao=cabine.data_impressao
    )
    
    # Aqui você persiste no banco
    db.session.add(cabine_bd)
    db.session.commit()

    return cabine_bd


def listar_cabines():
    return CabineModel.query.all()

def listar_cabine_by_id(cabine_id):
    return CabineModel.query.filter_by(id=cabine_id).first()

def deletar_cabine(cabine):
    db.session.delete(cabine)
    db.session.commit()

def atualizar_cabine(cabine_bd, cabine):
    cabine_bd.variedades = cabine.variedades
    cabine_bd.classificacao = cabine.classificacao
    cabine_bd.peso = cabine.peso
    cabine_bd.total_etiquetas = cabine.total_etiquetas
    cabine_bd.modelo_etiquetas = cabine.modelo_etiquetas
    cabine_bd.cabines = cabine.cabines
    cabine_bd.data_registro = cabine.data_registro or cabine_bd.data_registro
    cabine_bd.data_impressao = cabine.data_impressao
    db.session.commit()
    return cabine_bd