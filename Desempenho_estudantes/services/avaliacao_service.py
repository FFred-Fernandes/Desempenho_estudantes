from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.matricula_turma_repository import MatriculaTurmaRepository
from entities.models import Avaliacao
from datetime import datetime

class AvaliacaoService:
    @staticmethod
    def _atualizar_risco_nota_parcial(matricula):
        # REGRA 5: Classificação Automática de Risco por Nota.
        # O módulo de análise deve rotular como "Risco de Reprovação por Nota"
        # os alunos que apresentarem média parcial inferior a 5.0 nas avaliações já computadas.
        avaliacoes = matricula.avaliacoes
        if avaliacoes:
            media_parcial = sum(float(a.valor_nota) for a in avaliacoes) / len(avaliacoes)
            matricula.risco_nota = (media_parcial < 5.0)
        else:
            matricula.risco_nota = False
        MatriculaTurmaRepository.atualizar()

    @staticmethod
    def validar_data_registro(data_str):
        # REGRA 6: Consistência Temporal.
        # O sistema não deve permitir o registro de notas ou frequências com datas futuras em relação à data atual do servidor.
        # Permite datas atuais ou anteriores (datas retroativas).
        if not data_str:
            return True, datetime.now()

        formatos = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S']
        data_recebida = None
        for fmt in formatos:
            try:
                data_recebida = datetime.strptime(str(data_str).strip(), fmt)
                break
            except ValueError:
                continue

        if not data_recebida:
            return False, "Formato de data inválido. Use 'AAAA-MM-DD' (ex: 2026-10-25) ou 'DD/MM/AAAA'."

        agora = datetime.now()
        # Se a data for dia futuro em relação à data de hoje:
        if data_recebida.date() > agora.date():
            return False, "Violação da Regra 6 (Consistência Temporal): Não é permitido registrar notas ou frequências com datas futuras em relação à data atual do servidor."

        # Se for no dia de hoje com horário futuro explícito:
        if data_recebida.date() == agora.date() and data_recebida > agora:
            return False, "Violação da Regra 6 (Consistência Temporal): O horário informado está no futuro em relação ao horário do servidor."

        return True, data_recebida

    @staticmethod
    def criar_avaliacao(dados):
        # PARTE 3: Operação de cadastro de avaliação (POST)
        matricula = MatriculaTurmaRepository.buscar_por_id(dados.get('matricula_turma_id'))
        if not matricula:
            return {"erro": "Matrícula não encontrada."}, 404
        
        # REGRA 10: Proteção de Avaliação.
        # Um aluno classificado com status "Evasão" ou "Trancado" não pode ter novas notas inseridas.
        estudante = matricula.estudante
        if estudante.status in ['Evasão', 'Trancado']:
            return {
                "erro": f"Violação da Regra 10 (Proteção de Avaliação): Não é permitido inserir notas para estudante com status '{estudante.status}'."
            }, 400
        
        # REGRA 1: Validação de Notas.
        # O sistema não deve permitir notas com valor inferior a 0 (zero) ou superior a 10 (dez).
        try:
            valor_nota = float(dados.get('valor_nota', -1))
        except (ValueError, TypeError):
            return {"erro": "Nota inválida."}, 400

        if valor_nota < 0.0 or valor_nota > 10.0:
            return {"erro": "Violação da Regra 1 (Validação de Notas): A nota deve estar estritamente entre 0.0 e 10.0."}, 400
            
        # REGRA 6: Consistência Temporal (permite datas anteriores e atual, bloqueia datas futuras).
        valida, res_data = AvaliacaoService.validar_data_registro(dados.get('data_registro'))
        if not valida:
            return {"erro": res_data}, 400
        data_registro = res_data
            
        nova_avaliacao = Avaliacao(
            matricula_turma_id=matricula.id,
            valor_nota=valor_nota,
            data_registro=data_registro
        )
        salva = AvaliacaoRepository.salvar(nova_avaliacao)
        
        # REGRA 5: Recalcula a média parcial após inclusão da nova avaliação
        AvaliacaoService._atualizar_risco_nota_parcial(matricula)
            
        return {
            "mensagem": "Avaliação criada com sucesso!",
            "id": salva.id,
            "risco_nota_atualizado": matricula.risco_nota
        }, 201

    @staticmethod
    def listar_avaliacoes():
        # PARTE 3: Operação de seleção geral de avaliações (GET)
        avaliacoes = AvaliacaoRepository.buscar_todas()
        lista = [{
            "id": a.id, 
            "matricula_turma_id": a.matricula_turma_id, 
            "valor_nota": float(a.valor_nota), 
            "data_registro": a.data_registro.strftime("%Y-%m-%d %H:%M:%S") if a.data_registro else ""
        } for a in avaliacoes]
        return lista, 200

    @staticmethod
    def buscar_avaliacao_por_id(id):
        # PARTE 3: Operação de seleção individual de avaliação (GET por ID)
        a = AvaliacaoRepository.buscar_por_id(id)
        if not a:
            return {"erro": "Avaliação não encontrada."}, 404
        return {
            "id": a.id,
            "matricula_turma_id": a.matricula_turma_id,
            "valor_nota": float(a.valor_nota),
            "data_registro": a.data_registro.strftime("%Y-%m-%d %H:%M:%S") if a.data_registro else ""
        }, 200

    @staticmethod
    def atualizar_avaliacao(id, dados):
        # PARTE 3: Operação de edição de avaliação (PUT)
        avaliacao = AvaliacaoRepository.buscar_por_id(id)
        if not avaliacao:
            return {"erro": "Avaliação não encontrada."}, 404
        
        # REGRA 1: Validação de Notas na atualização
        if 'valor_nota' in dados:
            try:
                nova_nota = float(dados.get('valor_nota', avaliacao.valor_nota))
            except (ValueError, TypeError):
                return {"erro": "Nota inválida."}, 400

            if nova_nota < 0.0 or nova_nota > 10.0:
                return {"erro": "Violação da Regra 1 (Validação de Notas): A nota deve estar estritamente entre 0.0 e 10.0."}, 400
            avaliacao.valor_nota = nova_nota

        # REGRA 6: Consistência Temporal na atualização de data
        if 'data_registro' in dados and dados['data_registro']:
            valida, res_data = AvaliacaoService.validar_data_registro(dados['data_registro'])
            if not valida:
                return {"erro": res_data}, 400
            avaliacao.data_registro = res_data

        AvaliacaoRepository.atualizar()

        # REGRA 5: Recalcula o risco por nota após a alteração
        AvaliacaoService._atualizar_risco_nota_parcial(avaliacao.matricula_turma)

        return {"mensagem": "Avaliação atualizada com sucesso!"}, 200

    @staticmethod
    def deletar_avaliacao(id):
        # PARTE 3: Operação de exclusão de avaliação (DELETE)
        avaliacao = AvaliacaoRepository.buscar_por_id(id)
        if not avaliacao:
            return {"erro": "Avaliação não encontrada."}, 404
        
        matricula = avaliacao.matricula_turma
        AvaliacaoRepository.deletar(avaliacao)

        # REGRA 5: Recalcula o risco por nota após a remoção
        AvaliacaoService._atualizar_risco_nota_parcial(matricula)

        return {"mensagem": "Avaliação deletada com sucesso."}, 200
