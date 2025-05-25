from flask import Blueprint, request, jsonify, make_response, render_template
from api.models.config_model import ConfiguracaoModel
from api.schemas.config_schema import ConfiguracaoTexto, ConfiguracaoJSON
from api.service.config_service import (
    obter_configuracao_texto, obter_configuracao_json, 
    obter_todas_configuracoes, salvar_configuracao_texto, 
    salvar_configuracao_json, deletar_configuracao
)
from flask_jwt_extended import jwt_required
from api import db
from pydantic import ValidationError
import json

configuracao_bp = Blueprint('configuracao', __name__)

# Constantes
CAMPOS_TEXTO = ['url_site', 'usuario', 'senha']
CAMPOS_SELECT = ['tipo_caixa', 'produto', 'cliente', 'tipo_etiqueta', 'local_estoque', 'esteira', 'latada', 'processo_interno']


@configuracao_bp.route('/configuracoes', methods=['GET'])
def pagina_configuracoes():
    configuracoes = {}

    for campo in CAMPOS_TEXTO:
        configuracoes[campo] = obter_configuracao_texto(campo) or ''
    
    for campo in CAMPOS_SELECT:
        json_data = obter_configuracao_json(campo)
        configuracoes[f"{campo}_json"] = json.dumps(json_data) if json_data else ''

    return render_template('configuracoes.html', configuracoes=configuracoes)


@configuracao_bp.route('/configuracoes/salvar', methods=['POST'])
def salvar_configuracoes():
    dados = request.form.to_dict()
    erros = []

    for campo in CAMPOS_TEXTO:
        if campo in dados:
            salvar_configuracao_texto(campo, dados[campo])

    for campo in CAMPOS_SELECT:
        json_campo = f"{campo}_json"
        if json_campo in dados and dados[json_campo].strip():
            try:
                json_data = json.loads(dados[json_campo])
                salvar_configuracao_json(campo, json_data)
            except json.JSONDecodeError:
                erros.append(f"O campo {campo} não contém um JSON válido.")

    if erros:
        return make_response(jsonify({"sucesso": False, "erros": erros}), 400)
    
    return make_response(jsonify({"sucesso": True, "mensagem": "Configurações salvas com sucesso!"}), 200)


@configuracao_bp.route('/api/configuracoes', methods=['GET'])
def api_listar_configuracoes():
    configs = obter_todas_configuracoes()
    return make_response(jsonify([
        {
            "id": c.id,
            "chave": c.chave,
            "valor": c.valor,
            "valor_json": c.valor_json
        } for c in configs
    ]), 200)


@configuracao_bp.route('/api/configuracoes/<string:chave>', methods=['GET'])
def api_obter_configuracao(chave):
    valor_texto = obter_configuracao_texto(chave)
    valor_json = obter_configuracao_json(chave)

    if valor_texto is None and valor_json is None:
        return make_response(jsonify({"erro": "Configuração não encontrada"}), 404)

    return make_response(jsonify({
        "chave": chave,
        "valor": valor_texto,
        "valor_json": valor_json
    }), 200)


@configuracao_bp.route('/api/configuracoes/texto', methods=['POST'])
def api_salvar_configuracao_texto():
    try:
        dados = request.get_json()
        config_data = ConfiguracaoTexto(**dados)
        config = salvar_configuracao_texto(config_data.chave, config_data.valor)

        return make_response(jsonify({
            "id": config.id,
            "chave": config.chave,
            "valor": config.valor
        }), 201)
    except ValidationError as e:
        return make_response(jsonify({"erro": e.errors()}), 400)


@configuracao_bp.route('/api/configuracoes/json', methods=['POST'])
def api_salvar_configuracao_json():
    try:
        dados = request.get_json()
        config_data = ConfiguracaoJSON(**dados)
        config = salvar_configuracao_json(config_data.chave, config_data.valor_json)

        return make_response(jsonify({
            "id": config.id,
            "chave": config.chave,
            "valor_json": config.valor_json
        }), 201)
    except ValidationError as e:
        return make_response(jsonify({"erro": e.errors()}), 400)


@configuracao_bp.route('/api/configuracoes/<string:chave>', methods=['DELETE'])
def api_deletar_configuracao(chave):
    sucesso = deletar_configuracao(chave)

    if sucesso:
        return make_response(jsonify({"mensagem": f"Configuração '{chave}' removida com sucesso"}), 200)
    return make_response(jsonify({"erro": f"Configuração '{chave}' não encontrada"}), 404)
