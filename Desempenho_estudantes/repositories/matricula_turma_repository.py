from entities.models import MatriculaTurma, Turma
from config.database import db

class MatriculaTurmaRepository:
    @staticmethod
    def buscar_por_id(id):
        # PARTE 3: Busca de matrícula por ID
        return MatriculaTurma.query.get(id)

    @staticmethod
    def buscar_todas():
        # PARTE 3: Listagem de todas as matrículas
        return MatriculaTurma.query.all()

    @staticmethod
    def buscar_matricula_estudante_disciplina_semestre(estudante_id, disciplina_id, semestre, ano):
        # REGRA 3: Apoio à prevenção de duplicidade (mesmo aluno, mesma disciplina, mesmo semestre)
        return MatriculaTurma.query.join(MatriculaTurma.turma).filter(
            MatriculaTurma.estudante_id == estudante_id,
            Turma.disciplina_id == disciplina_id,
            Turma.semestre == semestre,
            Turma.ano == ano
        ).first()

    @staticmethod
    def salvar(matricula):
        # PARTE 3: Persistência de matrícula
        db.session.add(matricula)
        db.session.commit()
        return matricula

    @staticmethod
    def atualizar():
        # PARTE 3: Atualização no banco
        db.session.commit()

    @staticmethod
    def deletar(matricula):
        # PARTE 3: Exclusão de matrícula
        db.session.delete(matricula)
        db.session.commit()
