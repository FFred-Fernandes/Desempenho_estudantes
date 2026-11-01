from flask_restful import Resource
from flask import request
from services.disciplina_service import DisciplinaService

# PARTE 3: Operações CRUD completas (POST, GET, PUT, DELETE) para a entidade Disciplina
class DisciplinaController(Resource):
    def get(self, id=None):
        # PARTE 3: Suporta listagem geral ou seleção por ID
        if id:
            resposta, status_code = DisciplinaService.buscar_disciplina_por_id(id)
        else:
            resposta, status_code = DisciplinaService.listar_disciplinas()
        return resposta, status_code

    def post(self):
        # PARTE 3: Cadastro de disciplina (POST)
        dados = request.get_json()
        resposta, status_code = DisciplinaService.criar_disciplina(dados)
        return resposta, status_code

    def put(self, id):
        # PARTE 3: Atualização de disciplina (PUT)
        dados = request.get_json()
        resposta, status_code = DisciplinaService.atualizar_disciplina(id, dados)
        return resposta, status_code

    def delete(self, id):
        # PARTE 3: Exclusão de disciplina (DELETE) com validação histórica
        resposta, status_code = DisciplinaService.deletar_disciplina(id)
        return resposta, status_code
