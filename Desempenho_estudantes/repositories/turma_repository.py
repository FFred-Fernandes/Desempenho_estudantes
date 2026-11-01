from entities.models import Turma
from config.database import db

class TurmaRepository:
    @staticmethod
    def buscar_por_id(id):
        return Turma.query.get(id)

    @staticmethod
    def buscar_todas():
        return Turma.query.all()

    @staticmethod
    def salvar(turma):
        db.session.add(turma)
        db.session.commit()
        return turma

    @staticmethod
    def atualizar():
        db.session.commit()

    @staticmethod
    def deletar(turma):
        db.session.delete(turma)
        db.session.commit()