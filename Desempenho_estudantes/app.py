from flask import Flask
from flask_restful import Api
from config.database import configure_database, db

# PARTE 2: Importando os modelos SQLAlchemy para que sejam reconhecidos
from entities import models

# PARTE 3: Importando a inicialização de rotas do arquivo routes/api_routes.py
from routes.api_routes import inicializar_rotas

app = Flask(__name__)
api = Api(app)

# PARTE 3: Registra todos os endpoints da API (CRUD e analíticos)
inicializar_rotas(api)

# PARTE 2: Inicializando a conexão com o banco de dados PostgreSQL
configure_database(app)

# Rota de teste para confirmar que a API está no ar
@app.route('/')
def index():
    return {
        "sistema": "API de Análise de Desempenho de Estudantes",
        "disciplina": "Programação Avançada (PAV)",
        "status": "Online",
        "modulos": [
            "/estudantes",
            "/disciplinas",
            "/turmas",
            "/matriculas",
            "/avaliacoes",
            "/turmas/<id>/anomalia",
            "/turmas/<id>/fechamento"
        ]
    }

if __name__ == '__main__':
    with app.app_context():
        # Sincroniza os modelos com o banco PostgreSQL
        db.create_all()
    
    # Inicia o servidor Flask na porta 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
