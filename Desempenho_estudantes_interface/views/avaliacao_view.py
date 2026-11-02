# PARTE 4: Tela de lançamento de Avaliações usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import api_client as api

class AvaliacaoView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self._construir_tela()

    def _construir_tela(self):
        tk.Label(self, text="📝  Lançamento de Avaliações",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)

        # ── Formulário ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Dados da Avaliação",
                                   bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                   padx=10, pady=8)
        frame_form.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(frame_form, text="ID Matrícula:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_mat = tk.Entry(frame_form, width=10)
        self.entry_mat.grid(row=0, column=1, padx=6)

        tk.Label(frame_form, text="Nota (0 a 10):", bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.entry_nota = tk.Entry(frame_form, width=10)
        self.entry_nota.grid(row=0, column=3, padx=6)

        # REGRA 6: Controle de Consistência Temporal (permite datas anteriores/atuais, bloqueia futuras)
        tk.Label(frame_form, text="Data (AAAA-MM-DD):", bg="#f0f0f0").grid(row=0, column=4, sticky="w")
        self.entry_data = tk.Entry(frame_form, width=14)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=0, column=5, padx=6)

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Lançar Nota",    "#27ae60", self._lancar),
            ("✏️   Atualizar",      "#2980b9", self._atualizar),
            ("🗑️   Remover",       "#e74c3c", self._remover),
            ("🔄  Atualizar Lista","#7f8c8d", self._carregar),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"), width=16, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=5)

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        colunas = ("id", "matricula_turma_id", "valor_nota", "data_registro", "disciplina", "risco")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=14)

        headers = {
            "id": ("ID", 50), "matricula_turma_id": ("ID Matrícula", 120),
            "valor_nota": ("Nota", 80), "data_registro": ("Data de Registro (Regra 6)", 220),
            "disciplina": ("Disciplina", 120),
            "risco": ("Risco", 80)
        }
        for col, (label, w) in headers.items():
            self.tabela.heading(col, text=label)
            self.tabela.column(col, width=w, anchor="center")

        # Tag para destacar notas baixas (< 5)
        self.tabela.tag_configure("nota_baixa", background="#ffe0e0")
        self.tabela.tag_configure("nota_ok",    background="#e0ffe0")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_linha)

        self._carregar()
        self._criar_filtro_disciplina()

    def _carregar(self):
        """Carrega a lista completa de avaliações na tabela."""
        # 1️⃣ Limpar a tabela existente
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # 2️⃣ Atualizar o combobox de disciplinas (caso novas disciplinas tenham sido criadas)
        if hasattr(self, "combo_disciplina"):
            disciplinas = api.listar_disciplinas()
            nomes = ["Todas"] + [d["nome"] for d in disciplinas]
            self.combo_disciplina["values"] = nomes
            # Se a seleção atual não existir mais, volta para "Todas"
            if getattr(self, "disciplina_filtro", None) not in nomes:
                self.combo_disciplina.current(0)
                self.disciplina_filtro = "Todas"

        # 3️⃣ Construir mapeamento matrícula → disciplina
        self._map_disciplina = self._construir_mapeamento_disciplina()

        # 4️⃣ Inserir avaliações
        for a in api.listar_avaliacoes():
            nota = float(a["valor_nota"])
            tag = "nota_baixa" if nota < 5.0 else "nota_ok"
            disciplina = self._map_disciplina.get(a["matricula_turma_id"], "")
            
            if hasattr(self, "disciplina_filtro") and self.disciplina_filtro != "Todas" and disciplina != self.disciplina_filtro:
                continue
                
            risk_class = "Sim" if nota < 5 else "Não"
            
            self.tabela.insert(
                "",
                tk.END,
                values=(
                    a.get("id", ""),
                    a.get("matricula_turma_id", ""),
                    f"{nota:.1f}",
                    a.get("data_registro", ""),
                    disciplina or "",
                    risk_class or "",
                ),
                tags=(tag,)
            )
            
        # Atualiza o filtro se ele existir, para exibir as opções corretas
        if hasattr(self, "combo_disciplina"):
            self._criar_filtro_disciplina()

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_mat.delete(0, tk.END);  self.entry_mat.insert(0, v[1])
        self.entry_nota.delete(0, tk.END); self.entry_nota.insert(0, v[2])
        self.entry_data.delete(0, tk.END); self.entry_data.insert(0, v[3].split()[0] if v[3] else "")
        self._id_selecionado = v[0]

    def _lancar(self):
        try:
            # validar data digitada
            data_str = self.entry_data.get()
            try:
                data_obj = datetime.strptime(data_str, "%Y-%m-%d")
                if data_obj.date() > datetime.now().date():
                    messagebox.showwarning("Atenção", "Data não pode ser futura.")
                    return
            except ValueError:
                messagebox.showwarning("Atenção", "Formato de data inválido. Use AAAA-MM-DD.")
                return
            dados = {
                "matricula_turma_id": int(self.entry_mat.get()),
                "valor_nota":         float(self.entry_nota.get()),
                "data_registro": data_str
            }
        except ValueError:
            messagebox.showwarning("Atenção", "ID Matrícula deve ser inteiro e Nota deve ser decimal.")
            return
        resp, status = api.lancar_avaliacao(dados)
        if status == 201:
            risco = resp.get("risco_nota_atualizado", False)
            msg = resp.get("mensagem", "Nota lançada!")
            if risco:
                msg += "\n⚠ ATENÇÃO: Média parcial do aluno está abaixo de 5.0!"
            messagebox.showinfo("Sucesso", msg)
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao lançar nota."))

    def _atualizar(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma avaliação na tabela.")
            return
        try:
            # validar data digitada
            data_str = self.entry_data.get()
            try:
                data_obj = datetime.strptime(data_str, "%Y-%m-%d")
                if data_obj.date() > datetime.now().date():
                    messagebox.showwarning("Atenção", "Data não pode ser futura.")
                    return
            except ValueError:
                messagebox.showwarning("Atenção", "Formato de data inválido. Use AAAA-MM-DD.")
                return
            dados = {
                "valor_nota":    float(self.entry_nota.get()),
                "data_registro": data_str
            }
        except ValueError:
            messagebox.showwarning("Atenção", "Nota deve ser um número decimal válido.")
            return
        resp, status = api.atualizar_avaliacao(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Avaliação atualizada com sucesso!"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao atualizar."))

    def _remover(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma avaliação na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja remover esta avaliação?"):
            return
        resp, status = api.deletar_avaliacao(self._id_selecionado)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao remover."))

    def _limpar(self):
        self.entry_mat.delete(0, tk.END)
        self.entry_nota.delete(0, tk.END)
        self.entry_data.delete(0, tk.END); self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        # Reset disciplina filter selection to "Todas"
        if hasattr(self, "combo_disciplina"):
            self.combo_disciplina.set("Todas")
            self.disciplina_filtro = "Todas"
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

    def _construir_mapeamento_disciplina(self):
        """Constrói dicionário matricula_turma_id -> nome da disciplina."""
        matriculas = api.listar_matriculas()
        turmas = api.listar_turmas()
        disciplinas = api.listar_disciplinas()
        turma_id_to_disc_id = {t["id"]: t["disciplina_id"] for t in turmas}
        disc_id_to_nome = {d["id"]: d["nome"] for d in disciplinas}
        mapa = {}
        for m in matriculas:
            turma_id = m.get("turma_id")
            disc_id = turma_id_to_disc_id.get(turma_id)
            nome = disc_id_to_nome.get(disc_id, "")
            mapa[m["id"]] = nome
        return mapa

    def _criar_filtro_disciplina(self):
        """Cria dropdown para filtrar avaliações por disciplina."""
        # Evitar criar o frame múltiplas vezes se já existir
        if hasattr(self, "combo_disciplina"):
            return
            
        frame_filtro = tk.Frame(self, bg="#f0f0f0")
        frame_filtro.pack(fill=tk.X, pady=5)
        tk.Label(frame_filtro, text="Filtrar por Disciplina:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        disciplinas = api.listar_disciplinas()
        nomes = ["Todas"] + [d["nome"] for d in disciplinas]
        self.combo_disciplina = ttk.Combobox(frame_filtro, values=nomes, state="readonly")
        self.combo_disciplina.current(0)
        self.combo_disciplina.pack(side=tk.LEFT, padx=5)
        self.combo_disciplina.bind("<<ComboboxSelected>>", self._aplicar_filtro_disciplina)
        self.disciplina_filtro = "Todas"

    def _aplicar_filtro_disciplina(self, event=None):
        """Aplica o filtro selecionado e recarrega a lista."""
        self.disciplina_filtro = self.combo_disciplina.get()
        self._limpar()
        self._carregar()