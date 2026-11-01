from entities.models import Disciplina
from config.database import db

class DisciplinaRepository:
    @staticmethod
    def buscar_por_codigo(codigo):
        return Disciplina.query.filter_by(codigo=codigo).first()

    @staticmethod
    def buscar_por_id(id):
        return Disciplina.query.get(id)

    @staticmethod
    def buscar_todas():
        return Disciplina.query.all()

    @staticmethod
    def salvar(disciplina):
        db.session.add(disciplina)
        db.session.commit()
        return disciplina

    @staticmethod
    def atualizar():
        db.session.commit()

    @staticmethod
    def deletar(disciplina):
        db.session.delete(disciplina)
        db.session.commit()