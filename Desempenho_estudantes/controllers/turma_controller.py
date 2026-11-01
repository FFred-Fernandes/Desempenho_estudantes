from flask_restful import Resource
from flask import request
from services.turma_service import TurmaService

# PARTE 3: Operações CRUD completas (POST, GET, PUT, DELETE) para a entidade Turma
class TurmaController(Resource):
    def get(self, id=None):
        # PARTE 3: Suporta listagem geral ou seleção por ID
        if id:
            resposta, status_code = TurmaService.buscar_turma_por_id(id)
        else:
            resposta, status_code = TurmaService.listar_turmas()
        return resposta, status_code

    def post(self):
        # PARTE 3: Cadastro de turma (POST)
        dados = request.get_json()
        resposta, status_code = TurmaService.criar_turma(dados)
        return resposta, status_code

    def put(self, id):
        # PARTE 3: Atualização de turma (PUT)
        dados = request.get_json()
        resposta, status_code = TurmaService.atualizar_turma(id, dados)
        return resposta, status_code

    def delete(self, id):
        # PARTE 3: Exclusão de turma (DELETE)
        resposta, status_code = TurmaService.deletar_turma(id)
        return resposta, status_code

# PARTE 3 & REGRA 7: Endpoint analítico para detecção de anomalias na turma
class TurmaAnomaliaController(Resource):
    def get(self, turma_id):
        # REGRA 7: Detecção de Anomalia de Turma (< 30% do valor da prova)
        resposta, status_code = TurmaService.detectar_anomalia_turma(turma_id)
        return resposta, status_code
