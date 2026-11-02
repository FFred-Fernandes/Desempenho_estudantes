# PARTE 4: Ponto de entrada principal da Interface Gráfica usando Tkinter
# Este projeto é independente da API (Parte 3) e se comunica com ela via HTTP (requests)
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# Adiciona a pasta raiz no path para importar corretamente
sys.path.insert(0, os.path.dirname(__file__))

from views.inicio_view     import InicioView
from views.estudante_view  import EstudanteView
from views.disciplina_view import DisciplinaView
from views.turma_view      import TurmaView
from views.matricula_view  import MatriculaView
from views.avaliacao_view  import AvaliacaoView
from views.analise_view    import AnaliseView
import api_client as api

# ──────────────────────────────────────────────────────────────
# PARTE 4: Classe principal da aplicação (herança de tk.Tk)
# Aplica OO: herança, construtor e encapsulamento de componentes
# ──────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        # Construtor: inicializa a janela principal (herança de tk.Tk)
        super().__init__()
        self.title("Sistema de Análise de Desempenho de Estudantes | PAV")
        self.geometry("1120x700")
        self.resizable(True, True)
        self.configure(bg="#2c3e50")

        self.botoes_menu = {}
        self.telas_cache = {}
        self.tela_atual = None

        self._verificar_api()
        self._construir_interface()

    def _verificar_api(self):
        # Verifica se a API está rodando antes de abrir a interface
        try:
            import requests
            r = requests.get("http://127.0.0.1:5000/", timeout=3)
            if r.status_code != 200:
                raise ConnectionError
        except Exception:
            messagebox.showerror(
                "API Offline",
                "Não foi possível conectar à API.\n\n"
                "Certifique-se de que o servidor está rodando:\n"
                "  cd Desempenho_estudantes\n"
                "  python app.py"
            )

    def _construir_interface(self):
        # ── Cabeçalho ───────────────────────────────────────
        frame_header = tk.Frame(self, bg="#1a252f", pady=12)
        frame_header.pack(fill=tk.X)

        tk.Label(
            frame_header,
            text="🎓  Sistema de Análise de Desempenho de Estudantes",
            font=("Helvetica", 15, "bold"),
            bg="#1a252f",
            fg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            frame_header,
            text="Programação Avançada — PAV",
            font=("Helvetica", 10),
            bg="#1a252f",
            fg="#95a5a6"
        ).pack(side=tk.RIGHT, padx=20)

        # ── Container principal (sidebar + conteúdo) ────────
        frame_main = tk.Frame(self, bg="#2c3e50")
        frame_main.pack(fill=tk.BOTH, expand=True)

        # ── Sidebar de navegação ─────────────────────────────
        self.frame_sidebar = tk.Frame(frame_main, bg="#1a252f", width=195)
        self.frame_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_sidebar.pack_propagate(False)

        tk.Label(
            self.frame_sidebar,
            text="NAVEGAÇÃO",
            font=("Helvetica", 9, "bold"),
            bg="#1a252f",
            fg="#7f8c8d",
            pady=10
        ).pack(fill=tk.X, padx=10)

        ttk.Separator(self.frame_sidebar, orient="horizontal").pack(fill=tk.X, padx=10)

        # Itens do Menu com Tela Inicial incluída
        menus = [
            {"id": "inicio",      "texto": "🏠  Início / Menu",     "tela": InicioView},
            {"id": "estudantes",  "texto": "👩‍🎓  Estudantes",       "tela": EstudanteView},
            {"id": "disciplinas", "texto": "📚  Disciplinas",       "tela": DisciplinaView},
            {"id": "turmas",      "texto": "🏫  Turmas",            "tela": TurmaView},
            {"id": "matriculas",  "texto": "📋  Matrículas",        "tela": MatriculaView},
            {"id": "avaliacoes",  "texto": "📝  Avaliações",        "tela": AvaliacaoView},
            {"id": "analise",     "texto": "📊  Análise / Fechar",  "tela": AnaliseView},
        ]

        # ── Área de conteúdo à direita ──────────────────────
        self.frame_conteudo = tk.Frame(frame_main, bg="#f0f0f0")
        self.frame_conteudo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Estrutura de repetição para criar os botões da barra lateral
        for item in menus:
            btn = tk.Button(
                self.frame_sidebar,
                text=item["texto"],
                font=("Helvetica", 10),
                bg="#1a252f",
                fg="#ecf0f1",
                activebackground="#2980b9",
                activeforeground="white",
                bd=0,
                pady=10,
                cursor="hand2",
                anchor="w",
                padx=15,
                command=lambda chave=item["id"], cls=item["tela"]: self._trocar_tela_instantanea(chave, cls)
            )
            btn.pack(fill=tk.X)
            self.botoes_menu[item["id"]] = btn

        ttk.Separator(self.frame_sidebar, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            self.frame_sidebar,
            text="❌  Sair",
            font=("Helvetica", 10),
            bg="#c0392b",
            fg="white",
            activebackground="#e74c3c",
            bd=0,
            pady=8,
            cursor="hand2",
            command=self.quit
        ).pack(fill=tk.X)

        # Inicia abrindo a Tela de Início / Menu Principal
        self._trocar_tela_instantanea("inicio", InicioView)

    def _trocar_tela_instantanea(self, chave, TelaCls):
        # 1. Atualiza visual do botão ativo na barra lateral
        for b_id, btn in self.botoes_menu.items():
            if b_id == chave:
                btn.configure(bg="#2980b9", fg="#ffffff", font=("Helvetica", 10, "bold"))
            else:
                btn.configure(bg="#1a252f", fg="#ecf0f1", font=("Helvetica", 10))

        # 2. Oculta a tela visível atual instantaneamente (sem destruir os componentes)
        if self.tela_atual:
            self.tela_atual.pack_forget()

        # 3. Reutiliza ou instancia a tela no cache de memória
        recem_criada = False
        if chave not in self.telas_cache:
            if chave == "inicio":
                instancia = TelaCls(self.frame_conteudo, callback_navegacao=self._trocar_tela_instantanea)
            else:
                instancia = TelaCls(self.frame_conteudo)
            self.telas_cache[chave] = instancia
            recem_criada = True

        self.tela_atual = self.telas_cache[chave]
        self.tela_atual.pack(fill=tk.BOTH, expand=True)

        # 4. Atualiza os dados apenas se a tela já existia no cache
        # (na primeira vez, a tela já carrega os dados em seu próprio construtor)
        if not recem_criada:
            if hasattr(self.tela_atual, "_carregar_da_api"):
                self.after_idle(self.tela_atual._carregar_da_api)
            elif hasattr(self.tela_atual, "_carregar") and chave != "inicio":
                self.after_idle(self.tela_atual._carregar)


# ──────────────────────────────────────────────────────────────
# Ponto de entrada: inicia a aplicação Tkinter
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
