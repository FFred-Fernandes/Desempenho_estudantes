from config.database import db
from datetime import datetime

class Estudante(db.Model):
    __tablename__ = 'estudantes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    matriculas = db.relationship('MatriculaTurma', backref='estudante', lazy=True)

    # PARTE 3: Utilizar efetivamente conceitos de Orientação a Objetos (Construtores).
    def __init__(self, nome=None, cpf=None, matricula=None, status='Ativo', ativo=True, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.cpf = cpf
        self.matricula = matricula
        self.status = status
        self.ativo = ativo

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    total_avaliacoes_obrigatorias = db.Column(db.Integer, nullable=False, default=2)

    turmas = db.relationship('Turma', backref='disciplina', lazy=True)

    # PARTE 3: Utilizar efetivamente conceitos de Orientação a Objetos (Construtores).
    def __init__(self, codigo=None, nome=None, total_avaliacoes_obrigatorias=2, **kwargs):
        super().__init__(**kwargs)
        self.codigo = codigo
        self.nome = nome
        self.total_avaliacoes_obrigatorias = total_avaliacoes_obrigatorias

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    ano = db.Column(db.Integer, nullable=False)

    matriculas = db.relationship('MatriculaTurma', backref='turma', lazy=True)

    # PARTE 3: Utilizar efetivamente conceitos de Orientação a Objetos (Construtores).
    def __init__(self, disciplina_id=None, semestre=None, ano=None, **kwargs):
        super().__init__(**kwargs)
        self.disciplina_id = disciplina_id
        self.semestre = semestre
        self.ano = ano

class MatriculaTurma(db.Model):
    __tablename__ = 'matriculas_turma'
    id = db.Column(db.Integer, primary_key=True)
    # Mapeamento com nomes reais das colunas no PostgreSQL: 'estudantes_id' e 'frequencia_percetual'
    estudante_id = db.Column('estudantes_id', db.Integer, db.ForeignKey('estudantes.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    frequencia_percentual = db.Column('frequencia_percetual', db.Numeric(5, 2), nullable=False, default=100.00)
    risco_falta = db.Column(db.Boolean, nullable=False, default=False)
    risco_nota = db.Column(db.Boolean, nullable=False, default=False)
    data_registro = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    avaliacoes = db.relationship('Avaliacao', backref='matricula_turma', lazy=True)

    # PARTE 3: Utilizar efetivamente conceitos de Orientação a Objetos (Construtores).
    def __init__(self, estudante_id=None, turma_id=None, frequencia_percentual=100.00, risco_falta=False, risco_nota=False, data_registro=None, **kwargs):
        super().__init__(**kwargs)
        self.estudante_id = estudante_id
        self.turma_id = turma_id
        self.frequencia_percentual = frequencia_percentual
        self.risco_falta = risco_falta
        self.risco_nota = risco_nota
        if data_registro:
            self.data_registro = data_registro

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    id = db.Column(db.Integer, primary_key=True)
    matricula_turma_id = db.Column(db.Integer, db.ForeignKey('matriculas_turma.id'), nullable=False)
    valor_nota = db.Column(db.Numeric(4, 2), nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # PARTE 3: Utilizar efetivamente conceitos de Orientação a Objetos (Construtores).
    def __init__(self, matricula_turma_id=None, valor_nota=None, data_registro=None, **kwargs):
        super().__init__(**kwargs)
        self.matricula_turma_id = matricula_turma_id
        self.valor_nota = valor_nota
        if data_registro:
            self.data_registro = data_registro
