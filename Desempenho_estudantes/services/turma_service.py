from repositories.turma_repository import TurmaRepository
from repositories.disciplina_repository import DisciplinaRepository
from entities.models import Turma

class TurmaService:
    @staticmethod
    def validar_semestre(semestre):
        sem_str = str(semestre or '').strip()
        if sem_str not in ['1', '2']:
            return False, "O semestre deve ser obrigatoriamente '1' (1º Semestre) ou '2' (2º Semestre)."
        return True, sem_str

    @staticmethod
    def criar_turma(dados):
        # PARTE 3: Operação de cadastro de turma (POST)
        disciplina = DisciplinaRepository.buscar_por_id(dados.get('disciplina_id'))
        if not disciplina:
            return {"erro": "Disciplina não encontrada."}, 404

        valido_sem, res_sem = TurmaService.validar_semestre(dados.get('semestre'))
        if not valido_sem:
            return {"erro": res_sem}, 400

        try:
            ano = int(dados.get('ano', 0))
            if ano < 2000 or ano > 2100:
                return {"erro": "Ano letivo inválido."}, 400
        except (ValueError, TypeError):
            return {"erro": "O ano deve ser um número inteiro."}, 400
        
        nova_turma = Turma(
            disciplina_id=dados.get('disciplina_id'),
            semestre=res_sem,
            ano=ano
        )
        salva = TurmaRepository.salvar(nova_turma)
        return {"mensagem": "Turma criada com sucesso!", "id": salva.id}, 201

    @staticmethod
    def listar_turmas():
        # PARTE 3: Operação de seleção geral de turmas (GET)
        turmas = TurmaRepository.buscar_todas()
        lista = [{
            "id": t.id, 
            "disciplina_id": t.disciplina_id, 
            "disciplina_nome": t.disciplina.nome if getattr(t, 'disciplina', None) else "",
            "semestre": t.semestre, 
            "ano": t.ano
        } for t in turmas]
        return lista, 200

    @staticmethod
    def buscar_turma_por_id(id):
        # PARTE 3: Operação de seleção individual de turma (GET por ID)
        t = TurmaRepository.buscar_por_id(id)
        if not t:
            return {"erro": "Turma não encontrada."}, 404
        return {
            "id": t.id,
            "disciplina_id": t.disciplina_id,
            "disciplina_nome": t.disciplina.nome if getattr(t, 'disciplina', None) else "",
            "semestre": t.semestre,
            "ano": t.ano
        }, 200

    @staticmethod
    def atualizar_turma(id, dados):
        # PARTE 3: Operação de edição de turma (PUT)
        turma = TurmaRepository.buscar_por_id(id)
        if not turma:
            return {"erro": "Turma não encontrada."}, 404
        
        if 'semestre' in dados:
            valido_sem, res_sem = TurmaService.validar_semestre(dados.get('semestre'))
            if not valido_sem:
                return {"erro": res_sem}, 400
            turma.semestre = res_sem
        
        if 'ano' in dados:
            try:
                ano = int(dados.get('ano'))
                turma.ano = ano
            except (ValueError, TypeError):
                return {"erro": "Ano inválido."}, 400
        TurmaRepository.atualizar()
        return {"mensagem": "Turma atualizada com sucesso!"}, 200

    @staticmethod
    def deletar_turma(id):
        # PARTE 3: Operação de exclusão de turma (DELETE)
        turma = TurmaRepository.buscar_por_id(id)
        if not turma:
            return {"erro": "Turma não encontrada."}, 404

        # REGRA 8: Integridade Histórica.
        # Não permite deletar turma se ela já possuir matrículas vinculadas.
        if len(turma.matriculas) > 0:
            return {
                "erro": "R8: Não é permitido excluir turma que possui matrículas/histórico vinculado (Integridade Histórica)."
            }, 400

        TurmaRepository.deletar(turma)
        return {"mensagem": "Turma deletada com sucesso."}, 200

    @staticmethod
    def detectar_anomalia_turma(turma_id):
        # PARTE 3: Funcionalidade analítica e estatística exigida na especificação
        # REGRA 7: Detecção de Anomalia de Turma.
        # O sistema deve gerar um alerta analítico caso a média geral de uma turma inteira,
        # seja inferior a 30% do valor total da prova (< 3.0), indicando anomalia na dificuldade da prova ou ensino.
        turma = TurmaRepository.buscar_por_id(turma_id)
        if not turma:
            return {"erro": "Turma não encontrada."}, 404

        notas_validas = []
        for matricula in turma.matriculas:
            # REGRA 10: Proteção de Avaliação.
            # Alunos com status "Evasão" ou "Trancado" não entram nos cálculos estatísticos das médias da turma.
            if matricula.estudante.status in ['Evasão', 'Trancado']:
                continue

            for avaliacao in matricula.avaliacoes:
                notas_validas.append(float(avaliacao.valor_nota))

        if not notas_validas:
            return {
                "turma_id": turma_id,
                "alerta_anomalia": False,
                "mensagem": "Nenhuma avaliação computada para alunos ativos nesta turma ainda."
            }, 200

        media_turma = sum(notas_validas) / len(notas_validas)
        limite_anomalia = 3.0  # 30% de 10.0

        anomalia_detectada = media_turma < limite_anomalia

        return {
            "turma_id": turma_id,
            "total_notas_analisadas": len(notas_validas),
            "media_turma": round(media_turma, 2),
            "limite_anomalia_30_porcento": limite_anomalia,
            "alerta_anomalia": anomalia_detectada,
            "mensagem": (
                "R7: Alerta de Anomalia na Turma - Média geral da turma inferior a 30% do valor da prova!"
                if anomalia_detectada
                else "Desempenho da turma dentro da normalidade (sem anomalia detectada)."
            )
        }, 200
