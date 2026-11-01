from flask_restful import Resource
from flask import request
from services.matricula_turma_service import MatriculaTurmaService

# PARTE 3: Operações CRUD completas (POST, GET, PUT, DELETE) para a entidade MatriculaTurma
class MatriculaTurmaController(Resource):
    def get(self, id=None):
        # PARTE 3: Suporta listagem geral ou seleção por ID
        if id:
            resposta, status_code = MatriculaTurmaService.buscar_matricula_por_id(id)
        else:
            resposta, status_code = MatriculaTurmaService.listar_matriculas()
        return resposta, status_code

    def post(self):
        # PARTE 3: Realização de matrícula (POST)
        dados = request.get_json()
        resposta, status_code = MatriculaTurmaService.matricular(dados)
        return resposta, status_code

    def put(self, id):
        # PARTE 3: Atualização de frequência / risco (PUT)
        dados = request.get_json()
        resposta, status_code = MatriculaTurmaService.atualizar_frequencia(id, dados)
        return resposta, status_code

    def delete(self, id):
        # PARTE 3: Exclusão de matrícula (DELETE)
        resposta, status_code = MatriculaTurmaService.deletar_matricula(id)
        return resposta, status_code
