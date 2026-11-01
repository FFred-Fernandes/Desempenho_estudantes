from flask_restful import Resource
from services.fechamento_service import FechamentoService

# PARTE 3 & REGRA 9: Processamento analítico final do semestre
class FechamentoController(Resource):
    def post(self, turma_id):
        # REGRA 9: Executa o fechamento se 100% das notas estiverem preenchidas
        resposta, status_code = FechamentoService.fechar_semestre(turma_id)
        return resposta, status_code
