from api import db
from api import app
from sqlalchemy import func

class CabecalhoPalletModel(db.Model):
    __tablename__ = "cabecalhos_pallet"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)

    tipo_de_caixa = db.Column(db.Integer, nullable=False)
    tex_tipoCaixa = db.Column(db.String(100), nullable=False)

    des_produto = db.Column(db.Integer, nullable=False)
    tex_descProduto = db.Column(db.String(100), nullable=False)

    cliente = db.Column(db.Integer, nullable=False)
    tex_cliente = db.Column(db.String(100), nullable=False)

    tipo_de_etiqueta = db.Column(db.Integer, nullable=False)
    tex_tipoEtiqueta = db.Column(db.String(100), nullable=False)

    local_de_estoque = db.Column(db.Integer, nullable=False)
    tex_localEstoque = db.Column(db.String(100), nullable=False)

    processo_interno = db.Column(db.Integer, nullable=False)
    q_pallets = db.Column(db.Integer, nullable=False)

    data_criacao = db.Column(db.DateTime, nullable=False, default=func.now())

    # Relacionamento com itens do pallet
    itens = db.relationship('ItemPalletModel', backref='cabecalho', lazy=True, cascade="all, delete-orphan")


class ItemPalletModel(db.Model):
    __tablename__ = "itens_pallet"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)

    esteira = db.Column(db.Integer, nullable=False)
    tex_esteira = db.Column(db.String(100), nullable=False)

    latada = db.Column(db.String(100), nullable=False)
    q_caixas = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    calibre = db.Column(db.Integer, nullable=False)
    brix = db.Column(db.Integer, nullable=False)
    observacoes = db.Column(db.String(255), nullable=True)

    cabecalho_id = db.Column(db.Integer, db.ForeignKey('cabecalhos_pallet.id'), nullable=False)



with app.app_context():
    db.create_all()