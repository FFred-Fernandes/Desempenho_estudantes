from entities.models import Estudante
from config.database import db

class EstudanteRepository:
    @staticmethod
    def buscar_por_cpf(cpf):
        # Apoia a REGRA 3 (Prevenção de Duplicidade): Busca o aluno para garantir que o CPF é único.
        return Estudante.query.filter_by(cpf=cpf).first()

    @staticmethod
    def buscar_por_matricula(matricula):
        # Apoia a REGRA 3 (Prevenção de Duplicidade): Busca o aluno para garantir matrícula única.
        return Estudante.query.filter_by(matricula=matricula).first()

    @staticmethod
    def buscar_por_id(id):
        return Estudante.query.get(id)

    @staticmethod
    def buscar_todos():
        # Retorna todos os estudantes (ativos e inativos) para visualização e auditoria da Regra 8
        return Estudante.query.all()

    @staticmethod
    def buscar_todos_ativos():
        # Apoia a REGRA 8: Como fazemos exclusão lógica, as listagens do sistema
        # só devem retornar os alunos que estão com ativo=True.
        return Estudante.query.filter_by(ativo=True).all()

    @staticmethod
    def salvar(estudante):
        db.session.add(estudante)
        db.session.commit()
        return estudante

    @staticmethod
    def atualizar():
        db.session.commit()

    @staticmethod
    def inativar(estudante):
        # REGRA 8: Integridade Histórica. 
        # O sistema não permite a exclusão (DELETE no banco) de um aluno. 
        # Apenas inativamos o registro (exclusão lógica) trocando a flag 'ativo' para False.
        estudante.ativo = False
        db.session.commit()
