# PARTE 4: Módulo de comunicação com a API REST (Parte 3)
# Utiliza a biblioteca requests para fazer as requisições HTTP
import requests

BASE_URL = "http://localhost:5000"

# ─── Estudantes ────────────────────────────────────────────
def listar_estudantes():
    try:
        r = requests.get(f"{BASE_URL}/estudantes")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def cadastrar_estudante(dados):
    try:
        r = requests.post(f"{BASE_URL}/estudantes", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def atualizar_estudante(id, dados):
    try:
        r = requests.put(f"{BASE_URL}/estudantes/{id}", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def deletar_estudante(id):
    try:
        r = requests.delete(f"{BASE_URL}/estudantes/{id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

# ─── Disciplinas ───────────────────────────────────────────
def listar_disciplinas():
    try:
        r = requests.get(f"{BASE_URL}/disciplinas")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def cadastrar_disciplina(dados):
    try:
        r = requests.post(f"{BASE_URL}/disciplinas", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def atualizar_disciplina(id, dados):
    try:
        r = requests.put(f"{BASE_URL}/disciplinas/{id}", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def deletar_disciplina(id):
    try:
        r = requests.delete(f"{BASE_URL}/disciplinas/{id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

# ─── Turmas ────────────────────────────────────────────────
def listar_turmas():
    try:
        r = requests.get(f"{BASE_URL}/turmas")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def cadastrar_turma(dados):
    try:
        r = requests.post(f"{BASE_URL}/turmas", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def deletar_turma(id):
    try:
        r = requests.delete(f"{BASE_URL}/turmas/{id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

# ─── Matrículas ────────────────────────────────────────────
def listar_matriculas():
    try:
        r = requests.get(f"{BASE_URL}/matriculas")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def realizar_matricula(dados):
    try:
        r = requests.post(f"{BASE_URL}/matriculas", json=dados)
        try:
            return r.json(), r.status_code
        except Exception:
            return {"erro": r.text or f"Erro HTTP {r.status_code}"}, r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def atualizar_frequencia(id, dados):
    try:
        r = requests.put(f"{BASE_URL}/matriculas/{id}", json=dados)
        try:
            return r.json(), r.status_code
        except Exception:
            return {"erro": r.text or f"Erro HTTP {r.status_code}"}, r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def deletar_matricula(id):
    try:
        r = requests.delete(f"{BASE_URL}/matriculas/{id}")
        try:
            return r.json(), r.status_code
        except Exception:
            return {"erro": r.text or f"Erro HTTP {r.status_code}"}, r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

# ─── Avaliações ────────────────────────────────────────────
def listar_avaliacoes():
    try:
        r = requests.get(f"{BASE_URL}/avaliacoes")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def lancar_avaliacao(dados):
    try:
        r = requests.post(f"{BASE_URL}/avaliacoes", json=dados)
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def deletar_avaliacao(id):
    try:
        r = requests.delete(f"{BASE_URL}/avaliacoes/{id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

# ─── Análise / Fechamento ──────────────────────────────────
def verificar_anomalia(turma_id):
    try:
        r = requests.get(f"{BASE_URL}/turmas/{turma_id}/anomalia")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

def fechar_semestre(turma_id):
    try:
        r = requests.post(f"{BASE_URL}/turmas/{turma_id}/fechamento")
        return r.json(), r.status_code
    except Exception as e:
        return {"erro": str(e)}, 500

