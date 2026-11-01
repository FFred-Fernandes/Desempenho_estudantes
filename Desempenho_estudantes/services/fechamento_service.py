from repositories.turma_repository import TurmaRepository

class FechamentoService:
    @staticmethod
    def fechar_semestre(turma_id):
        # PARTE 3: Processamento e análise de dados (Além do CRUD básico exigido no trabalho)
        # REGRA 9: Pré-requisito de Análise Final.
        # A rotina de fechamento de semestre só pode ser executada se 100% das notas
        # obrigatórias da disciplina estiverem preenchidas e associadas aos alunos.
        turma = TurmaRepository.buscar_por_id(turma_id)
        if not turma:
            return {"erro": "Turma não encontrada."}, 404
            
        disciplina = turma.disciplina
        avaliacoes_exigidas = disciplina.total_avaliacoes_obrigatorias
        
        matriculas_ativas = []
        for matricula in turma.matriculas:
            # REGRA 10: Proteção de Avaliação.
            # Alunos com status 'Evasão' ou 'Trancado' não entram nos cálculos estatísticos da turma.
            if matricula.estudante.status in ['Evasão', 'Trancado']:
                continue
            
            matriculas_ativas.append(matricula)
            
            # REGRA 9: Verifica se 100% das notas obrigatórias foram lançadas
            if len(matricula.avaliacoes) < avaliacoes_exigidas:
                return {
                    "erro": "Violação da Regra 9 (Pré-requisito de Análise Final): Fechamento bloqueado. É obrigatório ter 100% das notas lançadas para alunos ativos.",
                    "estudante": matricula.estudante.nome,
                    "notas_lancadas": len(matricula.avaliacoes),
                    "notas_exigidas": avaliacoes_exigidas
                }, 400
                
        # Processamento analítico final do fechamento
        total_alunos = len(matriculas_ativas)
        if total_alunos == 0:
            return {"mensagem": "Semestre fechado. Não há alunos ativos matriculados nesta turma."}, 200

        medias_finais = []
        aprovados = 0
        reprovados = 0

        for m in matriculas_ativas:
            media_aluno = sum(float(a.valor_nota) for a in m.avaliacoes) / len(m.avaliacoes)
            medias_finais.append(media_aluno)
            if media_aluno >= 5.0 and not m.risco_falta:
                aprovados += 1
            else:
                reprovados += 1

        media_geral_turma = sum(medias_finais) / total_alunos

        return {
            "mensagem": "Semestre fechado com sucesso! Processamento de dados finais concluído.",
            "turma_id": turma.id,
            "disciplina": disciplina.nome,
            "total_alunos_avaliados": total_alunos,
            "media_geral_turma": round(media_geral_turma, 2),
            "aprovados": aprovados,
            "reprovados": reprovados
        }, 200
