from entities.models import Avaliacao
from config.database import db

class AvaliacaoRepository:
    @staticmethod
    def buscar_por_id(id):
        return Avaliacao.query.get(id)

    @staticmethod
    def buscar_todas():
        return Avaliacao.query.all()

    @staticmethod
    def salvar(avaliacao):
        db.session.add(avaliacao)
        db.session.commit()
        return avaliacao

    @staticmethod
    def atualizar():
        db.session.commit()

    @staticmethod
    def deletar(avaliacao):
        db.session.delete(avaliacao)
        db.session.commit()