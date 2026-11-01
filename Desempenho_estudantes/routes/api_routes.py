# PARTE 3: Centralização de todas as rotas da API na camada routes/
from controllers.estudante_controller import EstudanteController
from controllers.disciplina_controller import DisciplinaController
from controllers.turma_controller import TurmaController, TurmaAnomaliaController
from controllers.matricula_turma_controller import MatriculaTurmaController
from controllers.avaliacao_controller import AvaliacaoController
from controllers.fechamento_controller import FechamentoController

def inicializar_rotas(api):
    # PARTE 3: Endpoints REST para cadastro (POST), seleção (GET), edição (PUT) e exclusão (DELETE) de cada tabela
    api.add_resource(EstudanteController, '/estudantes', '/estudantes/<int:id>')
    api.add_resource(DisciplinaController, '/disciplinas', '/disciplinas/<int:id>')
    api.add_resource(TurmaController, '/turmas', '/turmas/<int:id>')
    api.add_resource(MatriculaTurmaController, '/matriculas', '/matriculas/<int:id>')
    api.add_resource(AvaliacaoController, '/avaliacoes', '/avaliacoes/<int:id>')

    # PARTE 3 (Funcionalidades Analíticas de Ciência de Dados / Além do CRUD básico):
    # REGRA 7: Detecção de anomalia na média da turma (< 30% do valor da prova)
    api.add_resource(TurmaAnomaliaController, '/turmas/<int:turma_id>/anomalia')

    # REGRA 9: Pré-requisito de análise final e rotina de fechamento de semestre
    api.add_resource(FechamentoController, '/turmas/<int:turma_id>/fechamento')

