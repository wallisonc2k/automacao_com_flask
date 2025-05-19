from flask import Flask, render_template
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import get_local_ip


app = Flask(__name__)
app.config.from_pyfile('config.py')

api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

from api.models import pallet_model
from api.controller import pallet_controller

app.register_blueprint(pallet_controller.pallet_bp, url_prefix='/api')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/configuracao")
def configuracao():
    return render_template('configuracao.html')

@app.route("/pallets")
def pallets():
    ip = get_local_ip()
    variedades = ["Arra 15", "White Seedless", "Sugar Crisp", "IFG Eleven", "Autumn Crisp","White Seedless 02", "Sweet Celebration", "IFG Three"]
    return render_template("pallets.html", api_url_ip=ip)