from flask_restful import Resource
from flask import request
from services.estudante_service import EstudanteService

# PARTE 3: Operações CRUD completas (POST, GET, PUT, DELETE) para a entidade Estudante
class EstudanteController(Resource):
    def get(self, id=None):
        # PARTE 3: Suporta listagem de todos ou seleção por ID
        if id:
            resposta, status_code = EstudanteService.buscar_estudante_por_id(id)
        else:
            resposta, status_code = EstudanteService.listar_estudantes()
        return resposta, status_code

    def post(self):
        # PARTE 3: Cadastro (POST)
        dados = request.get_json()
        resposta, status_code = EstudanteService.criar_estudante(dados)
        return resposta, status_code

    def put(self, id):
        # PARTE 3: Atualização (PUT)
        dados = request.get_json()
        resposta, status_code = EstudanteService.atualizar_estudante(id, dados)
        return resposta, status_code

    def delete(self, id):
        # PARTE 3: Exclusão lógica (DELETE)
        resposta, status_code = EstudanteService.deletar_estudante(id)
        return resposta, status_code
