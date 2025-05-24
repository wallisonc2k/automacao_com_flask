from flask import Blueprint, request, jsonify, make_response
from api.models.pallet_model import CabecalhoPalletModel, ItemPalletModel
from api.schemas.pallet_schema import CabecalhoPallet, ItemPallet, RegistroPallet
from api.service.pallet_service import (
    cadastrar_pallet, listar_pallets, listar_pallet_by_id, listar_itens_pallet,
    deletar_pallet, atualizar_pallet, adicionar_item_pallet, remover_item_pallet,
    buscar_pallets_por_filtros, valores_para_filtros
)
#from api.paginate import paginate
from flask_jwt_extended import jwt_required
from datetime import datetime
from pydantic import ValidationError
from api.automacao import RegistroPalletManager

pallet_bp = Blueprint('pallet', __name__)


@pallet_bp.route('/pallets', methods=['POST'])
def criar_pallet():
    """
    Cria um novo pallet com seus itens
    """
    try:
        dados = request.get_json()
        
        # Usar Pydantic para validação
        try:
            registro_pallet = RegistroPallet(**dados)
        except ValidationError as e:
            return make_response(jsonify({"message": "Dados inválidos", "errors": e.errors()}), 400)
            
        # Converter para objetos do SQLAlchemy para persistência
        cabecalho = CabecalhoPalletModel(
            tipo_de_caixa=registro_pallet.cabecalho.tipo_de_caixa,
            tex_tipoCaixa=registro_pallet.cabecalho.tex_tipoCaixa,
            des_produto=registro_pallet.cabecalho.des_produto,
            tex_descProduto=registro_pallet.cabecalho.tex_descProduto,
            cliente=registro_pallet.cabecalho.cliente,
            tex_cliente=registro_pallet.cabecalho.tex_cliente,
            tipo_de_etiqueta=registro_pallet.cabecalho.tipo_de_etiqueta,
            tex_tipoEtiqueta=registro_pallet.cabecalho.tex_tipoEtiqueta,
            local_de_estoque=registro_pallet.cabecalho.local_de_estoque,
            tex_localEstoque=registro_pallet.cabecalho.tex_localEstoque,
            processo_interno=registro_pallet.cabecalho.processo_interno
        )
        
        itens = []
        for item_data in registro_pallet.itens:
            item = ItemPalletModel(
                esteira=item_data.esteira,
                tex_esteira=item_data.tex_esteira,
                latada=item_data.latada,
                q_caixas=item_data.q_caixas,
                cor=item_data.cor,
                calibre=item_data.calibre,
                brix=item_data.brix,
                observacoes=item_data.observacoes
            )
            itens.append(item)
        
        # Cadastrar no banco
        resultado = cadastrar_pallet(cabecalho, itens)
        
        # Converter de volta para resposta
        response_data = {
            "id": resultado.id,
            "tipo_de_caixa": resultado.tipo_de_caixa,
            "tex_tipoCaixa": resultado.tex_tipoCaixa,
            "des_produto": resultado.des_produto,
            "tex_descProduto": resultado.tex_descProduto,
            "cliente": resultado.cliente,
            "tex_cliente": resultado.tex_cliente,
            "tipo_de_etiqueta": resultado.tipo_de_etiqueta,
            "tex_tipoEtiqueta": resultado.tex_tipoEtiqueta,
            "local_de_estoque": resultado.local_de_estoque, 
            "tex_localEstoque": resultado.tex_localEstoque,
            "processo_interno": resultado.processo_interno,
            "data_criacao": resultado.data_criacao.isoformat() if resultado.data_criacao else None
        }
        
        # Retornar resposta
        return make_response(
            jsonify({
                "message": "Pallet cadastrado com sucesso",
                "data": response_data
            }), 201
        )
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao cadastrar pallet",
                "error": str(e)
            }), 500
        )


@pallet_bp.route('/pallets', methods=['GET'])
def obter_pallets():
    """
    Lista pallets com opção de filtros e paginação
    """
    try:
        cliente = request.args.get('cliente', type=int)
        tipo_de_caixa = request.args.get('tipo_de_caixa', type=int)
        data_inicial_str = request.args.get('data_inicial')
        data_final_str = request.args.get('data_final')

        data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d') if data_inicial_str else None
        data_final = datetime.strptime(data_final_str, '%Y-%m-%d') if data_final_str else None
        if data_final:
            data_final = data_final.replace(hour=23, minute=59, second=59)

        if cliente or tipo_de_caixa or data_inicial or data_final:
            pallets = buscar_pallets_por_filtros(cliente, tipo_de_caixa, data_inicial, data_final)
        else:
            pallets = listar_pallets()

        filtros = valores_para_filtros()
        

        resultado = []
        for p in pallets:
            itens_bd = listar_itens_pallet(p.id)
            itens_list = [
                {
                    "id": item.id,
                    "esteira": item.esteira,
                    "tex_esteira": item.tex_esteira,
                    "latada": item.latada,
                    "q_caixas": item.q_caixas,
                    "cor": item.cor,
                    "calibre": item.calibre,
                    "brix": item.brix,
                    "observacoes": item.observacoes
                }
                for item in itens_bd
            ]

            resultado.append({
                "id": p.id,
                "cabecalho": {
                    "tipo_de_caixa": p.tipo_de_caixa,
                    "tex_tipoCaixa": p.tex_tipoCaixa,
                    "des_produto": p.des_produto,
                    "tex_descProduto": p.tex_descProduto,
                    "cliente": p.cliente,
                    "tex_cliente": p.tex_cliente,
                    "tipo_de_etiqueta": p.tipo_de_etiqueta,
                    "tex_tipoEtiqueta": p.tex_tipoEtiqueta,
                    "local_de_estoque": p.local_de_estoque,
                    "tex_localEstoque": p.tex_localEstoque,
                    "processo_interno": p.processo_interno
                },
                "itens": itens_list,
                "data_criacao": p.data_criacao.isoformat() if p.data_criacao else None
            })

        return make_response(jsonify({"pallets": resultado, "filtros": filtros}), 200)

    except Exception as e:
        return make_response(jsonify({
            "message": "Erro ao listar pallets",
            "error": str(e)
        }), 500)


@pallet_bp.route('/pallets/<int:id>', methods=['GET'])
def obter_pallet(id):
    """
    Obtém um pallet específico pelo ID
    """
    try:
        pallet = listar_pallet_by_id(id)
        
        if not pallet:
            return make_response(
                jsonify({
                    "message": f"Pallet com ID {id} não encontrado"
                }), 404
            )
        
        # Obter itens do pallet
        itens_bd = listar_itens_pallet(id)
        
        # Converter cabeçalho para dicionário
        cabecalho_dict = {
            "tipo_de_caixa": pallet.tipo_de_caixa,
            "tex_tipoCaixa": pallet.tex_tipoCaixa,
            "des_produto": pallet.des_produto,
            "tex_descProduto": pallet.tex_descProduto,
            "cliente": pallet.cliente,
            "tex_cliente": pallet.tex_cliente,
            "tipo_de_etiqueta": pallet.tipo_de_etiqueta,
            "tex_tipoEtiqueta": pallet.tex_tipoEtiqueta,
            "local_de_estoque": pallet.local_de_estoque, 
            "tex_localEstoque": pallet.tex_localEstoque,
            "processo_interno": pallet.processo_interno
        }
        
        # Converter itens para dicionários
        itens_list = []
        for item in itens_bd:
            itens_list.append({
                "id": item.id,
                "esteira": item.esteira,
                "tex_esteira": item.tex_esteira,
                "latada": item.latada,
                "q_caixas": item.q_caixas,
                "cor": item.cor,
                "calibre": item.calibre,
                "brix": item.brix,
                "observacoes": item.observacoes
            })
        
        # Montar resposta com cabeçalho e itens
        result = {
            "id": pallet.id,
            "cabecalho": cabecalho_dict,
            "itens": itens_list
        }
        
        return make_response(jsonify(result), 200)
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao obter pallet",
                "error": str(e)
            }), 500
        )


@pallet_bp.route('/pallets/<int:id>', methods=['PUT'])
def atualizar_pallet_route(id):
    """
    Atualiza um pallet existente
    """
    try:
        pallet_bd = listar_pallet_by_id(id)
        
        if not pallet_bd:
            return make_response(
                jsonify({
                    "message": f"Pallet com ID {id} não encontrado"
                }), 404
            )
        
        dados = request.get_json()
        
        # Validar dados usando Pydantic
        try:
            registro_pallet = RegistroPallet(**dados)
        except ValidationError as e:
            return make_response(jsonify({"message": "Dados inválidos", "errors": e.errors()}), 400)
        
        # Converter para objetos do SQLAlchemy
        cabecalho_novo = CabecalhoPalletModel(
            tipo_de_caixa=registro_pallet.cabecalho.tipo_de_caixa,
            tex_tipoCaixa=registro_pallet.cabecalho.tex_tipoCaixa,
            des_produto=registro_pallet.cabecalho.des_produto,
            tex_descProduto=registro_pallet.cabecalho.tex_descProduto,
            cliente=registro_pallet.cabecalho.cliente,
            tex_cliente=registro_pallet.cabecalho.tex_cliente,
            tipo_de_etiqueta=registro_pallet.cabecalho.tipo_de_etiqueta,
            tex_tipoEtiqueta=registro_pallet.cabecalho.tex_tipoEtiqueta,
            local_de_estoque=registro_pallet.cabecalho.local_de_estoque,
            tex_localEstoque=registro_pallet.cabecalho.tex_localEstoque,
            processo_interno=registro_pallet.cabecalho.processo_interno
        )
        
        itens_novos = []
        for item_data in registro_pallet.itens:
            item = ItemPalletModel(
                esteira=item_data.esteira,
                tex_esteira=item_data.tex_esteira,
                latada=item_data.latada,
                q_caixas=item_data.q_caixas,
                cor=item_data.cor,
                calibre=item_data.calibre,
                brix=item_data.brix,
                observacoes=item_data.observacoes
            )
            itens_novos.append(item)
        
        # Atualizar no banco
        resultado = atualizar_pallet(pallet_bd, cabecalho_novo, itens_novos)
        
        # Obter itens atualizados
        itens_bd = listar_itens_pallet(id)
        
        # Converter para resposta
        cabecalho_dict = {
            "id": resultado.id,
            "tipo_de_caixa": resultado.tipo_de_caixa,
            "tex_tipoCaixa": resultado.tex_tipoCaixa,
            "des_produto": resultado.des_produto,
            "tex_descProduto": resultado.tex_descProduto,
            "cliente": resultado.cliente,
            "tex_cliente": resultado.tex_cliente,
            "tipo_de_etiqueta": resultado.tipo_de_etiqueta,
            "tex_tipoEtiqueta": resultado.tex_tipoEtiqueta,
            "local_de_estoque": resultado.local_de_estoque, 
            "tex_localEstoque": resultado.tex_localEstoque,
            "processo_interno": resultado.processo_interno
        }
        
        # Converter itens para dicionários
        itens_list = []
        for item in itens_bd:
            itens_list.append({
                "id": item.id,
                "esteira": item.esteira,
                "tex_esteira": item.tex_esteira,
                "latada": item.latada,
                "q_caixas": item.q_caixas,
                "cor": item.cor,
                "calibre": item.calibre,
                "brix": item.brix,
                "observacoes": item.observacoes
            })
        
        # Montar resposta
        result = {
            "message": "Pallet atualizado com sucesso",
            "cabecalho": cabecalho_dict,
            "itens": itens_list
        }
        
        return make_response(jsonify(result), 200)
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao atualizar pallet",
                "error": str(e)
            }), 500
        )


@pallet_bp.route('/pallets/<int:id>', methods=['DELETE'])
def deletar_pallet_route(id):
    """
    Remove um pallet
    """
    try:
        pallet = listar_pallet_by_id(id)
        
        if not pallet:
            return make_response(
                jsonify({
                    "message": f"Pallet com ID {id} não encontrado"
                }), 404
            )
        
        deletar_pallet(pallet)
        
        return make_response(
            jsonify({
                "message": f"Pallet com ID {id} removido com sucesso"
            }), 200
        )
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao deletar pallet",
                "error": str(e)
            }), 500
        )


@pallet_bp.route('/pallets/<int:pallet_id>/itens', methods=['POST'])
def adicionar_item(pallet_id):
    """
    Adiciona um novo item a um pallet existente
    """
    try:
        pallet = listar_pallet_by_id(pallet_id)
        
        if not pallet:
            return make_response(
                jsonify({
                    "message": f"Pallet com ID {pallet_id} não encontrado"
                }), 404
            )
        
        dados = request.get_json()
        
        # Validar dados usando Pydantic
        try:
            item_data = ItemPallet(**dados)
        except ValidationError as e:
            return make_response(jsonify({"message": "Dados inválidos", "errors": e.errors()}), 400)
        
        # Converter para modelo SQLAlchemy
        item = ItemPalletModel(
            esteira=item_data.esteira,
            tex_esteira=item_data.tex_esteira,
            latada=item_data.latada,
            q_caixas=item_data.q_caixas,
            cor=item_data.cor,
            calibre=item_data.calibre,
            brix=item_data.brix,
            observacoes=item_data.observacoes
        )
        
        # Adicionar item
        resultado = adicionar_item_pallet(pallet_id, item)
        
        # Converter para resposta
        item_dict = {
            "id": resultado.id,
            "esteira": resultado.esteira,
            "tex_esteira": resultado.tex_esteira,
            "latada": resultado.latada,
            "q_caixas": resultado.q_caixas,
            "cor": resultado.cor,
            "calibre": resultado.calibre,
            "brix": resultado.brix,
            "observacoes": resultado.observacoes
        }
        
        return make_response(
            jsonify({
                "message": "Item adicionado com sucesso",
                "data": item_dict
            }), 201
        )
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao adicionar item ao pallet",
                "error": str(e)
            }), 500
        )


@pallet_bp.route('/pallets/itens/<int:item_id>', methods=['DELETE'])
def remover_item(item_id):
    """
    Remove um item específico de um pallet
    """
    try:
        resultado = remover_item_pallet(item_id)
        
        if not resultado:
            return make_response(
                jsonify({
                    "message": f"Item com ID {item_id} não encontrado"
                }), 404
            )
        AutomacaoRegistroPallet
        return make_response(
            jsonify({
                "message": f"Item com ID {item_id} removido com sucesso"
            }), 200
        )
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao remover item do pallet",
                "error": str(e)
            }), 500
        )

@pallet_bp.route('/pallets/lancar_pallet_gvssystem', methods=['POST'])
def lancar_pallet_gvssystem():
    """
    Cria usa selenium para lancar o pallet no GvsSystem
    """
    try:
        dados = request.get_json()
        
        # Usar Pydantic para validação
        try:
            registro_pallet = RegistroPallet(**dados)
        except ValidationError as e:
            return make_response(jsonify({"message": "Dados inválidos", "errors": e.errors()}), 400)

        # Iniciando automaçao
        try:
            automacao = RegistroPalletManager()
            automacao.realizar_lancamento_pallet(registro_pallet)

        except Exception as e:
            return make_response(jsonify({"message": "Problema no automacao.py", "errors": e.errors()}), 400)
 
        # Retornar resposta
        return make_response(
            jsonify({
                "message": "Pallet lançado com sucesso",
                "data": dados
            }), 200
        )
    
    except Exception as e:
        return make_response(
            jsonify({
                "message": "Erro ao cadastrar pallet",
                "error": str(e)
            }), 500
        )