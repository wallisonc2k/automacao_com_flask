from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from api import db
from api import app

class ConfiguracaoModel(db.Model):
    __tablename__ = 'configuracoes'

    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(1000), nullable=True)
    valor_json = db.Column(db.JSON, nullable=True)  # <-- Mudei de JSONB para JSON
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, chave, valor=None, valor_json=None):
        self.chave = chave
        self.valor = valor
        self.valor_json = valor_json


# Criação das tabelas no contexto do app
with app.app_context():
    db.create_all()
