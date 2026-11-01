from flask_sqlalchemy import SQLAlchemy

# Instância central do SQLAlchemy
db = SQLAlchemy()

def configure_database(app):
    # Substitua 'sua_senha' pela senha do seu usuário 'postgres' no banco local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123456@localhost:5432/desempenho_estudantes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)