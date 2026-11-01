from repositories.matricula_turma_repository import MatriculaTurmaRepository
from repositories.estudante_repository import EstudanteRepository
from repositories.turma_repository import TurmaRepository
from entities.models import MatriculaTurma

class MatriculaTurmaService:
    @staticmethod
    def matricular(dados):
        # PARTE 3: Operação de cadastro de matrícula (POST)
        estudante = EstudanteRepository.buscar_por_id(dados.get('estudante_id'))
        turma = TurmaRepository.buscar_por_id(dados.get('turma_id'))
        
        if not estudante or not turma:
            return {"erro": "Estudante ou Turma não encontrados."}, 404
            
        if not estudante.ativo:
            return {"erro": "Não é possível matricular estudante inativo."}, 400

        # REGRA 3: Prevenção de Duplicidade.
        # O sistema não deve permitir que o aluno seja matriculado mais de uma vez
        # na mesma disciplina durante o mesmo semestre letivo.
        ja_matriculado = MatriculaTurmaRepository.buscar_matricula_estudante_disciplina_semestre(
            estudante_id=estudante.id,
            disciplina_id=turma.disciplina_id,
            semestre=turma.semestre,
            ano=turma.ano
        )
        if ja_matriculado:
            return {
                "erro": "Violação da Regra 3 (Prevenção de Duplicidade): O aluno já está matriculado nesta mesma disciplina durante o semestre letivo atual."
            }, 400

        frequencia_inicial = float(dados.get('frequencia_percentual', 100.00))
        # REGRA 2: Validação de Frequência.
        # Não aceitar frequências negativas ou superiores a 100%.
        if frequencia_inicial < 0.0 or frequencia_inicial > 100.0:
            return {"erro": "Violação da Regra 2 (Validação de Frequência): A frequência não pode ser negativa nem superior a 100%."}, 400

        # REGRA 4: Classificação Automática de Risco por Falta.
        # Classifica com risco crítico quando frequência estiver abaixo de 75%.
        risco_falta = frequencia_inicial < 75.0

        nova_matricula = MatriculaTurma(
            estudante_id=estudante.id,
            turma_id=turma.id,
            frequencia_percentual=frequencia_inicial,
            risco_falta=risco_falta
        )
        salva = MatriculaTurmaRepository.salvar(nova_matricula)
        return {"mensagem": "Matrícula realizada com sucesso!", "id": salva.id}, 201

    @staticmethod
    def listar_matriculas():
        # PARTE 3: Operação de seleção geral de matrículas (GET)
        matriculas = MatriculaTurmaRepository.buscar_todas()
        lista = [{
            "id": m.id, 
            "estudante_id": m.estudante_id, 
            "turma_id": m.turma_id,
            "frequencia_percentual": float(m.frequencia_percentual),
            "risco_falta": m.risco_falta,
            "risco_nota": m.risco_nota
        } for m in matriculas]
        return lista, 200

    @staticmethod
    def buscar_matricula_por_id(id):
        # PARTE 3: Operação de seleção individual de matrícula (GET por ID)
        m = MatriculaTurmaRepository.buscar_por_id(id)
        if not m:
            return {"erro": "Matrícula não encontrada."}, 404
        return {
            "id": m.id,
            "estudante_id": m.estudante_id,
            "turma_id": m.turma_id,
            "frequencia_percentual": float(m.frequencia_percentual),
            "risco_falta": m.risco_falta,
            "risco_nota": m.risco_nota
        }, 200

    @staticmethod
    def atualizar_frequencia(id, dados):
        # PARTE 3: Operação de edição de matrícula (PUT)
        matricula = MatriculaTurmaRepository.buscar_por_id(id)
        if not matricula:
            return {"erro": "Matrícula não encontrada."}, 404
        
        try:
            nova_frequencia = float(dados.get('frequencia_percentual', matricula.frequencia_percentual))
        except (ValueError, TypeError):
            return {"erro": "Frequência inválida."}, 400

        # REGRA 2: Validação de Frequência.
        # O sistema não deve aceitar registro de frequências negativas ou superiores a 100%.
        if nova_frequencia < 0.0 or nova_frequencia > 100.0:
            return {"erro": "Violação da Regra 2 (Validação de Frequência): A frequência deve estar entre 0% e 100%."}, 400

        matricula.frequencia_percentual = nova_frequencia

        # REGRA 4: Classificação Automática de Risco por Falta.
        # Classificar com flag "Risco Crítico por Falta" qualquer aluno cuja frequência caia abaixo de 75%.
        matricula.risco_falta = (nova_frequencia < 75.0)
        
        MatriculaTurmaRepository.atualizar()
        return {
            "mensagem": "Dados da matrícula atualizados com sucesso!",
            "frequencia": float(matricula.frequencia_percentual),
            "risco_falta": matricula.risco_falta
        }, 200

    @staticmethod
    def deletar_matricula(id):
        # PARTE 3: Operação de exclusão de matrícula (DELETE)
        matricula = MatriculaTurmaRepository.buscar_por_id(id)
        if not matricula:
            return {"erro": "Matrícula não encontrada."}, 404
        MatriculaTurmaRepository.deletar(matricula)
        return {"mensagem": "Matrícula deletada com sucesso."}, 200
