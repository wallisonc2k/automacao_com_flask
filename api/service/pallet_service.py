from api import db
from api.models.pallet_model import CabecalhoPalletModel, ItemPalletModel
from sqlalchemy import func
from datetime import datetime
from typing import List

def cadastrar_pallet(cabecalho, itens):
    """
    Cadastra um novo pallet com seu cabeçalho e itens
    
    Args:
        cabecalho: Dados do cabeçalho do pallet
        itens: Lista de itens do pallet
    
    Returns:
        CabecalhoPalletModel: Objeto do pallet cadastrado
    """
    # Criar o cabeçalho do pallet
    cabecalho_bd = CabecalhoPalletModel(
        tipo_de_caixa=cabecalho.tipo_de_caixa,
        tex_tipoCaixa=cabecalho.tex_tipoCaixa,
        des_produto=cabecalho.des_produto,
        tex_descProduto=cabecalho.tex_descProduto,
        cliente=cabecalho.cliente,
        tex_cliente=cabecalho.tex_cliente,
        tipo_de_etiqueta=cabecalho.tipo_de_etiqueta,
        tex_tipoEtiqueta=cabecalho.tex_tipoEtiqueta,
        local_de_estoque=cabecalho.local_de_estoque,
        tex_localEstoque=cabecalho.tex_localEstoque,
        processo_interno=cabecalho.processo_interno,
        data_criacao=datetime.now()
    )
    
    db.session.add(cabecalho_bd)
    db.session.flush()  # Para obter o ID gerado sem commitar ainda
    
    # Adicionar cada item do pallet
    for item in itens:
        item_bd = ItemPalletModel(
            esteira=item.esteira,
            tex_esteira=item.tex_esteira,
            latada=item.latada,
            q_caixas=item.q_caixas,
            cor=item.cor,
            calibre=item.calibre,
            brix=item.brix,
            observacoes=item.observacoes,
            cabecalho_id=cabecalho_bd.id
        )
        db.session.add(item_bd)
    
    # Commitar todas as mudanças
    db.session.commit()
    
    return cabecalho_bd


def listar_pallets():
    """
    Lista todos os pallets cadastrados
    
    Returns:
        list: Lista de todos os cabeçalhos de pallets
    """
    return CabecalhoPalletModel.query.all()


def listar_pallet_by_id(pallet_id):
    """
    Busca um pallet específico pelo ID
    
    Args:
        pallet_id: ID do pallet a ser buscado
    
    Returns:
        CabecalhoPalletModel: Objeto do pallet encontrado ou None
    """
    return CabecalhoPalletModel.query.filter_by(id=pallet_id).first()


def listar_itens_pallet(pallet_id):
    """
    Lista todos os itens de um pallet específico
    
    Args:
        pallet_id: ID do pallet
    
    Returns:
        list: Lista dos itens do pallet
    """
    return ItemPalletModel.query.filter_by(cabecalho_id=pallet_id).all()


def deletar_pallet(pallet):
    """
    Remove um pallet do banco de dados
    
    Args:
        pallet: Objeto pallet a ser removido
    """
    db.session.delete(pallet)
    db.session.commit()


def atualizar_pallet(pallet_bd, pallet_novo, itens_novos=None):
    """
    Atualiza os dados de um pallet existente
    
    Args:
        pallet_bd: Objeto pallet existente no banco
        pallet_novo: Objeto com os novos dados do pallet
        itens_novos: Lista opcional com novos itens
    
    Returns:
        CabecalhoPalletModel: Objeto do pallet atualizado
    """
    # Atualizar dados do cabeçalho
    pallet_bd.tipo_de_caixa = pallet_novo.tipo_de_caixa
    pallet_bd.tex_tipoCaixa = pallet_novo.tex_tipoCaixa
    pallet_bd.des_produto = pallet_novo.des_produto
    pallet_bd.tex_descProduto = pallet_novo.tex_descProduto
    pallet_bd.cliente = pallet_novo.cliente
    pallet_bd.tex_cliente = pallet_novo.tex_cliente
    pallet_bd.tipo_de_etiqueta = pallet_novo.tipo_de_etiqueta
    pallet_bd.tex_tipoEtiqueta = pallet_novo.tex_tipoEtiqueta
    pallet_bd.local_de_estoque = pallet_novo.local_de_estoque
    pallet_bd.tex_localEstoque = pallet_novo.tex_localEstoque
    pallet_bd.processo_interno = pallet_novo.processo_interno
    
    # Se novos itens foram fornecidos, atualizar também
    if itens_novos is not None:
        # Remover itens existentes
        ItemPalletModel.query.filter_by(cabecalho_id=pallet_bd.id).delete()
        
        # Adicionar novos itens
        for item in itens_novos:
            item_bd = ItemPalletModel(
                esteira=item.esteira,
                tex_esteira=item.tex_esteira,
                latada=item.latada,
                q_caixas=item.q_caixas,
                cor=item.cor,
                calibre=item.calibre,
                brix=item.brix,
                observacoes=item.observacoes,
                cabecalho_id=pallet_bd.id
            )
            db.session.add(item_bd)
    
    db.session.commit()
    return pallet_bd


def adicionar_item_pallet(pallet_id, item):
    """
    Adiciona um novo item a um pallet existente
    
    Args:
        pallet_id: ID do pallet
        item: Dados do novo item
    
    Returns:
        ItemPalletModel: Objeto do item adicionado
    """
    item_bd = ItemPalletModel(
        esteira=item.esteira,
        tex_esteira=item.tex_esteira,
        latada=item.latada,
        q_caixas=item.q_caixas,
        cor=item.cor,
        calibre=item.calibre,
        brix=item.brix,
        observacoes=item.observacoes,
        cabecalho_id=pallet_id
    )
    
    db.session.add(item_bd)
    db.session.commit()
    
    return item_bd


def remover_item_pallet(item_id):
    """
    Remove um item específico de um pallet
    
    Args:
        item_id: ID do item a ser removido
    
    Returns:
        bool: True se o item foi removido com sucesso
    """
    item = ItemPalletModel.query.filter_by(id=item_id).first()
    
    if item:
        db.session.delete(item)
        db.session.commit()
        return True
    
    return False


def buscar_pallets_por_filtros(cliente=None, tipo_de_caixa=None, data_inicial=None, data_final=None):
    """
    Busca pallets com base em filtros específicos
    
    Args:
        cliente: ID do cliente (opcional)
        tipo_de_caixa: ID do tipo_de_caixa (opcional)
        data_inicial: Data inicial para filtro (opcional)
        data_final: Data final para filtro (opcional)
    
    Returns:
        list: Lista de pallets que correspondem aos filtros
    """
    query = CabecalhoPalletModel.query
    
    if cliente:
        query = query.filter(CabecalhoPalletModel.cliente == cliente)
    
    if tipo_de_caixa:
        query = query.filter(CabecalhoPalletModel.tipo_de_caixa == tipo_de_caixa)
    
    if data_inicial:
        query = query.filter(CabecalhoPalletModel.data_criacao >= data_inicial)
    
    if data_final:
        query = query.filter(CabecalhoPalletModel.data_criacao <= data_final)
    
    return query.all()
