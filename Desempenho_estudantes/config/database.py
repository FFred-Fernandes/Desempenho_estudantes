import os
from flask_sqlalchemy import SQLAlchemy

# Instância central do SQLAlchemy
db = SQLAlchemy()

def configure_database(app):
    # Configuração da conexão com o banco PostgreSQL
    # Pode ser definida via variável de ambiente DATABASE_URL ou usar o padrão abaixo:
    default_uri = 'postgresql+psycopg2://postgres:123456@localhost:5432/desempenho_estudantes'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)