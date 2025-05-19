from api import db
from api import app
from sqlalchemy import func

class CabineModel(db.Model):
    __tablename__ = "cabines"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    variedades = db.Column(db.String(100), nullable=False)
    classificacao = db.Column(db.String(100), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    total_etiquetas = db.Column(db.Integer, nullable=False)
    modelo_etiquetas = db.Column(db.String(100), nullable=False)
    cabines = db.Column(db.JSON, nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=func.now())
    data_impressao = db.Column(db.DateTime, nullable=True)


with app.app_context():
    db.create_all()