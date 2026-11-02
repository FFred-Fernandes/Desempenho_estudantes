import re
from repositories.disciplina_repository import DisciplinaRepository
from entities.models import Disciplina

class DisciplinaService:
    @staticmethod
    def validar_nome_disciplina(nome):
        nome_str = str(nome or '').strip()
        if not nome_str:
            return False, "O nome da disciplina não pode estar vazio."
        # Não pode conter dígitos numéricos
        if re.search(r'\d', nome_str):
            return False, "O nome da disciplina não pode conter números/dígitos."
        return True, nome_str

    @staticmethod
    def criar_disciplina(dados):
        # PARTE 3: Operação de cadastro (POST)
        nome = dados.get('nome')
        valido_nome, res_nome = DisciplinaService.validar_nome_disciplina(nome)
        if not valido_nome:
            return {"erro": res_nome}, 400

        if DisciplinaRepository.buscar_por_codigo(dados.get('codigo')):
            return {"erro": "Disciplina com este código já está cadastrada."}, 400
        
        nova_disciplina = Disciplina(
            codigo=str(dados.get('codigo')).strip(),
            nome=res_nome,
            total_avaliacoes_obrigatorias=dados.get('total_avaliacoes_obrigatorias', 2)
        )
        salva = DisciplinaRepository.salvar(nova_disciplina)
        return {"mensagem": "Disciplina criada com sucesso!", "id": salva.id}, 201

    @staticmethod
    def listar_disciplinas():
        # PARTE 3: Operação de seleção múltipla (GET)
        disciplinas = DisciplinaRepository.buscar_todas()
        lista = [{"id": d.id, "codigo": d.codigo, "nome": d.nome, "avaliacoes_obrigatorias": d.total_avaliacoes_obrigatorias} for d in disciplinas]
        return lista, 200

    @staticmethod
    def buscar_disciplina_por_id(id):
        # PARTE 3: Operação de seleção individual (GET por ID)
        disciplina = DisciplinaRepository.buscar_por_id(id)
        if not disciplina:
            return {"erro": "Disciplina não encontrada."}, 404
        return {
            "id": disciplina.id,
            "codigo": disciplina.codigo,
            "nome": disciplina.nome,
            "avaliacoes_obrigatorias": disciplina.total_avaliacoes_obrigatorias
        }, 200

    @staticmethod
    def atualizar_disciplina(id, dados):
        # PARTE 3: Operação de edição (PUT)
        disciplina = DisciplinaRepository.buscar_por_id(id)
        if not disciplina:
            return {"erro": "Disciplina não encontrada."}, 404
        
        if 'nome' in dados:
            valido_nome, res_nome = DisciplinaService.validar_nome_disciplina(dados.get('nome'))
            if not valido_nome:
                return {"erro": res_nome}, 400
            disciplina.nome = res_nome
        disciplina.total_avaliacoes_obrigatorias = dados.get('total_avaliacoes_obrigatorias', disciplina.total_avaliacoes_obrigatorias)
        
        DisciplinaRepository.atualizar()
        return {"mensagem": "Disciplina atualizada com sucesso!"}, 200

    @staticmethod
    def deletar_disciplina(id):
        # PARTE 3: Operação de exclusão (DELETE)
        disciplina = DisciplinaRepository.buscar_por_id(id)
        if not disciplina:
            return {"erro": "Disciplina não encontrada."}, 404
        
        # REGRA 8: Integridade Histórica.
        # O sistema não deve permitir a exclusão (DELETE no banco) de uma disciplina que já possua histórico/turmas vinculadas.
        if len(disciplina.turmas) > 0:
            return {
                "erro": "Violação da Regra 8 (Integridade Histórica): A disciplina possui turmas/histórico vinculado e não pode ser excluída fisicamente."
            }, 400
        
        DisciplinaRepository.deletar(disciplina)
        return {"mensagem": "Disciplina deletada com sucesso."}, 200
