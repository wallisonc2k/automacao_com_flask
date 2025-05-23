import os
import sys
from flask import Flask, render_template
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import get_local_ip

def resource_path(relative_path):
    """Obter caminho absoluto para recursos, funciona para dev e para PyInstaller"""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_database_path():
    """Retorna o caminho do banco de dados no diretório do executável"""
    if getattr(sys, 'frozen', False):
        # Se está rodando como executável
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, 'database.db')
    else:
        # Se está rodando em desenvolvimento
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

# Configurar Flask com caminhos corretos para templates e static
template_dir = resource_path('api/templates')
static_dir = resource_path('api/static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Configurar banco de dados com caminho dinâmico
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{get_database_path()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Adicione uma chave secreta
app.config['JWT_SECRET_KEY'] = 'sua-jwt-chave-secreta'  # Para JWT

# Outras configurações do config.py se necessário
app.config['DEBUG'] = False  # Desabilitar debug em produção

api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

# Importar modelos e controladores
from api.models import pallet_model, config_model
from api.controller import pallet_controller, config_controller

# Registrar blueprints
app.register_blueprint(pallet_controller.pallet_bp, url_prefix='/api')
app.register_blueprint(config_controller.configuracao_bp)

def create_tables():
    """Criar tabelas do banco de dados se não existirem"""
    with app.app_context():
        db.create_all()
        print(f"Banco de dados criado/verificado em: {get_database_path()}")

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/pallets")
def pallets():
    ip = get_local_ip()
    variedades = ["Arra 15", "White Seedless", "Sugar Crisp", "IFG Eleven", 
                  "Autumn Crisp", "White Seedless 02", "Sweet Celebration", "IFG Three"]
    return render_template("pallets.html", api_url_ip=ip)

# Inicializar banco na primeira execução
create_tables()