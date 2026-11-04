# PARTE 4: Tela de Início / Menu Principal com guia das abas e rolagem do mouse
import tkinter as tk
from tkinter import ttk

class InicioView(tk.Frame):
    def __init__(self, master, callback_navegacao=None):
        super().__init__(master, bg="#f8fafc")
        self.callback_navegacao = callback_navegacao
        self._construir_tela()

    def _construir_tela(self):
        # ── Banner de Apresentação Superior ────────────────
        frame_banner = tk.Frame(self, bg="#1e293b", padx=30, pady=22)
        frame_banner.pack(fill=tk.X)

        tk.Label(
            frame_banner,
            text="🎓 Sistema de Análise de Desempenho Acadêmico",
            font=("Helvetica", 19, "bold"),
            bg="#1e293b",
            fg="#f8fafc"
        ).pack(anchor="w")

        tk.Label(
            frame_banner,
            text="Plataforma de Gestão e Monitoramento de Alunos, Turmas, Frequências e Notas",
            font=("Helvetica", 12),
            bg="#1e293b",
            fg="#94a3b8"
        ).pack(anchor="w", pady=(6, 0))

        # ── Área com Scrollbar e suporte ao Scroll do Mouse ──
        canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8fafc", padx=30, pady=20)

        # Ajusta a largura e a área de rolagem dinamicamente
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width - 10)

        scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        # ── Ativa a Rolagem com a Rodinha do Mouse (MouseWheel) ──
        def _on_mousewheel(event):
            # No Windows, event.delta é múltiplo de 120
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Título dos Módulos com Fonte Maior ──────────────
        tk.Label(
            scrollable_frame,
            text="📌 Módulos e Funcionalidades de Cada Aba:",
            font=("Helvetica", 15, "bold"),
            bg="#f8fafc",
            fg="#0f172a"
        ).pack(anchor="w", pady=(0, 14))

        modulos = [
            {
                "icone": "👩‍🎓",
                "titulo": "Estudantes",
                "cor_borda": "#3b82f6",
                "destaque": "Cadastro & Situação",
                "desc": "Permite cadastrar novos alunos com CPF e matrícula únicos. Permite inativar (exclusão lógica sem apagar o histórico) e alternar o status acadêmico entre Ativo, Trancado ou Evasão."
            },
            {
                "icone": "📚",
                "titulo": "Disciplinas",
                "cor_borda": "#8b5cf6",
                "destaque": "Currículo & Exigências",
                "desc": "Cadastra as matérias oferecidas e define o número total de avaliações obrigatórias exigidas no semestre. Protege disciplinas com turmas vinculadas contra exclusão acidental."
            },
            {
                "icone": "🏫",
                "titulo": "Turmas",
                "cor_borda": "#06b6d4",
                "destaque": "Ofertas Semestrais",
                "desc": "Organiza as disciplinas em períodos letivos específicos por semestre e ano. É a estrutura central onde os alunos se matriculam e realizam as avaliações."
            },
            {
                "icone": "📋",
                "titulo": "Matrículas",
                "cor_borda": "#10b981",
                "destaque": "Frequência & Alerta de Falta",
                "desc": "Inscreve alunos nas turmas (bloqueando matrículas duplicadas). Monitora a frequência percentual e classifica automaticamente alunos com Risco por Falta quando a frequência for inferior a 75%."
            },
            {
                "icone": "📝",
                "titulo": "Avaliações",
                "cor_borda": "#f59e0b",
                "destaque": "Notas & Alerta de Média",
                "desc": "Lança notas de 0 a 10 com verificação de datas futuras. Calcula em tempo real a média parcial do aluno e dispara o alerta Risco por Nota se a média estiver abaixo de 5.0."
            },
            {
                "icone": "📊",
                "titulo": "Análise / Fechamento",
                "cor_borda": "#ef4444",
                "destaque": "Inteligência & Encerramento",
                "desc": "Identifica se a média geral da turma está abaixo de 30% da prova (anomalia de ensino/dificuldade). Executa o fechamento oficial do semestre somente após 100% das notas estarem lançadas."
            }
        ]

        # Renderiza os cards organizados com fonte maior e espaçamentos confortáveis
        for m in modulos:
            card = tk.Frame(scrollable_frame, bg="#ffffff", padx=18, pady=16, relief=tk.SOLID, bd=1)
            card.pack(fill=tk.X, pady=7)

            # Barra lateral colorida do card
            barra_cor = tk.Frame(card, bg=m["cor_borda"], width=6)
            barra_cor.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

            frame_conteudo_card = tk.Frame(card, bg="#ffffff")
            frame_conteudo_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Cabeçalho do card
            header_card = tk.Frame(frame_conteudo_card, bg="#ffffff")
            header_card.pack(fill=tk.X)

            tk.Label(
                header_card,
                text=f"{m['icone']}  {m['titulo']}",
                font=("Helvetica", 13, "bold"),
                bg="#ffffff",
                fg="#0f172a"
            ).pack(side=tk.LEFT)

            tk.Label(
                header_card,
                text=m["destaque"],
                font=("Helvetica", 10, "bold"),
                bg="#f1f5f9",
                fg=m["cor_borda"],
                padx=10,
                pady=3
            ).pack(side=tk.RIGHT)

            # Descrição do card com fonte aumentada (tamanho 11)
            tk.Label(
                frame_conteudo_card,
                text=m["desc"],
                font=("Helvetica", 11),
                bg="#ffffff",
                fg="#334155",
                wraplength=820,
                justify=tk.LEFT
            ).pack(anchor="w", pady=(8, 0))

        # Espaço no final da rolagem
        tk.Frame(scrollable_frame, height=25, bg="#f8fafc").pack()
