from flask_restful import Resource
from flask import request
from services.avaliacao_service import AvaliacaoService

# PARTE 3: Operações CRUD completas (POST, GET, PUT, DELETE) para a entidade Avaliacao
class AvaliacaoController(Resource):
    def get(self, id=None):
        # PARTE 3: Suporta listagem geral ou seleção por ID
        if id:
            resposta, status_code = AvaliacaoService.buscar_avaliacao_por_id(id)
        else:
            resposta, status_code = AvaliacaoService.listar_avaliacoes()
        return resposta, status_code

    def post(self):
        # PARTE 3: Lançamento de nota (POST)
        dados = request.get_json()
        resposta, status_code = AvaliacaoService.criar_avaliacao(dados)
        return resposta, status_code

    def put(self, id):
        # PARTE 3: Atualização de nota (PUT)
        dados = request.get_json()
        resposta, status_code = AvaliacaoService.atualizar_avaliacao(id, dados)
        return resposta, status_code

    def delete(self, id):
        # PARTE 3: Exclusão de nota (DELETE)
        resposta, status_code = AvaliacaoService.deletar_avaliacao(id)
        return resposta, status_code
