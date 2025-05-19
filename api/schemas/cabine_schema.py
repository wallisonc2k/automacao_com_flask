from api import ma
from api.models.cabine_model import CabineModel
from marshmallow import fields

class CabineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CabineModel
        load_instance = True
        fields = ("id", "variedades", "classificacao", "peso",
                  "total_etiquetas", "modelo_etiquetas", "cabines",
                  "data_registro", "data_impressao")

    # Definição dos campos
    id = fields.Int(dump_only=True)  # dump_only para evitar que o ID seja incluído na criação de novos registros
    variedades = fields.String(required=True)
    classificacao = fields.String(required=True)
    peso = fields.Float(required=True)
    total_etiquetas = fields.Integer(required=True)
    modelo_etiquetas = fields.String(required=True)
    
    # Se cabines for uma lista de strings (ao invés de JSON genérico)
    cabines = fields.List(fields.String(), required=True)
    
    data_registro = fields.DateTime(dump_only=True)  # dump_only para apenas leitura
    data_impressao = fields.DateTime(allow_none=True)  # allow_none para permitir nulos no caso de não impressão ainda
