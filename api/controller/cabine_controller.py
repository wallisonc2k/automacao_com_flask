from flask_restful import Resource
from flask import request, make_response, jsonify
from api import api, automacao
from api.schemas.cabine_schema import CabineSchema
from api.service.cabine_service import (
    cadastrar_cabine,
    deletar_cabine,
    listar_cabine_by_id,
    listar_cabines,
    atualizar_cabine
)


class CabineController(Resource):
    def get(self):
        cabines = listar_cabines()
        cabine_json = CabineSchema(many=True).jsonify(cabines)
        return make_response(cabine_json, 200)

    def post(self):
        cabine = request.json
        validate = CabineSchema().validate(cabine)

        if validate:
            return make_response(jsonify(validate), 400)
        else:
            cabine = CabineSchema().load(cabine)
            cabine_bd = cadastrar_cabine(cabine)
            cabine_json = CabineSchema().jsonify(cabine_bd)
            return make_response(cabine_json, 201)

    def put(self, id):
        cabine = listar_cabine_by_id(id)
        if cabine is None:
            return make_response(jsonify({"message": "Cabine not found"}), 404)

        validate = CabineSchema().validate(request.json)
        if validate:
            return make_response(jsonify(validate), 400)
        else:
            novo_cabine = CabineSchema().load(request.json)
            cabine_bd = atualizar_cabine(cabine, novo_cabine)
            cabine_json = CabineSchema().jsonify(cabine_bd)
            return make_response(cabine_json, 200)

    def delete(self, id):
        cabine = listar_cabine_by_id(id)
        if cabine is None:
            return make_response(jsonify({"message": "Cabine not found"}), 404)
        deletar_cabine(cabine)
        return make_response("Cabine deleted", 204)


class CabineDetailController(Resource):
    def get(self, id):
        cabine = listar_cabine_by_id(id)
        if cabine is None:
            return make_response(jsonify({"message": "Código para Cabine nao encontrado"}), 404)
        cabine_json = CabineSchema().jsonify(cabine)
        return make_response(cabine_json, 200)


class CabineProcessController(Resource):
    def get(self, id):
        cabine = listar_cabine_by_id(id)
        if cabine is None:
            return make_response(jsonify({"message": "Código para Cabine nao encontrado"}), 404)
        cabine_json = CabineSchema().jsonify(cabine)

        r = automacao.Cabines("gerson.carlos", "BISCOITAODASORTE")
        r.preencher(cabine_json)

        return make_response(cabine_json, 200)


api.add_resource(CabineController, '/api/cabines')
api.add_resource(CabineController, '/api/cabines/<int:id>', endpoint='excluir_alterar_cabines', methods=['PUT', "DELETE"])
api.add_resource(CabineDetailController, '/api/cabines/<int:id>', methods=["GET"])
api.add_resource(CabineProcessController, '/api/cabines/<int:id>/imprimir', endpoint="imprimir", methods=["GET"])