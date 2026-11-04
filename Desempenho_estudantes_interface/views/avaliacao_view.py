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
            ("🗑️   Remover",        "#e74c3c", self._remover),
            ("🔄  Atualizar Lista", "#7f8c8d", self._carregar),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"), width=16, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=5)

        # ── Filtro por Disciplina ────────────────────────────
        self._criar_filtro_disciplina()

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        colunas = ("id", "matricula_turma_id", "valor_nota", "data_registro", "disciplina", "risco")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=14)

        headers = {
            "id": ("ID", 50),
            "matricula_turma_id": ("ID Matrícula", 120),
            "valor_nota": ("Nota (R1)", 90),
            "data_registro": ("Data de Registro (R6)", 200),
            "disciplina": ("Disciplina", 150),
            "risco": ("⚠ Risco de Nota (R5)", 130)
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

    def _carregar(self):
        """Carrega a lista completa de avaliações na tabela."""
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        if hasattr(self, "combo_disciplina"):
            disciplinas = api.listar_disciplinas()
            nomes = ["Todas"] + [d["nome"] for d in disciplinas]
            self.combo_disciplina["values"] = nomes
            if getattr(self, "disciplina_filtro", None) not in nomes:
                self.combo_disciplina.current(0)
                self.disciplina_filtro = "Todas"

        self._map_disciplina = self._construir_mapeamento_disciplina()
        matriculas_dict = {m["id"]: m for m in api.listar_matriculas()}

        avaliacoes = api.listar_avaliacoes()
        for a in avaliacoes:
            mat_id = a.get("matricula_turma_id")
            nome_disc = self._map_disciplina.get(mat_id, "")

            # Aplicar filtro por disciplina se selecionado
            filtro = getattr(self, "disciplina_filtro", "Todas")
            if filtro != "Todas" and nome_disc != filtro:
                continue

            nota = float(a.get("valor_nota", 0.0))
            tag = "nota_baixa" if nota < 5.0 else "nota_ok"

            m_info = matriculas_dict.get(mat_id, {})
            risco_nota_txt = "⚠ SIM" if m_info.get("risco_nota") else "NÃO"

            self.tabela.insert("", tk.END,
                               values=(a.get("id"), mat_id, f"{nota:.1f}", a.get("data_registro", ""), nome_disc, risco_nota_txt),
                               tags=(tag,))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_mat.delete(0, tk.END);  self.entry_mat.insert(0, v[1])
        self.entry_nota.delete(0, tk.END); self.entry_nota.insert(0, v[2])
        self.entry_data.delete(0, tk.END); self.entry_data.insert(0, v[3].split()[0] if v[3] else "")
        self._id_selecionado = v[0]

    def _validar_data_input(self, data_str):
        formatos = ['%Y-%m-%d', '%d/%m/%Y']
        data_obj = None
        for fmt in formatos:
            try:
                data_obj = datetime.strptime(data_str, fmt)
                break
            except ValueError:
                continue

        if not data_obj:
            return False, "Formato de data inválido. Use AAAA-MM-DD (ex: 2026-11-03) ou DD/MM/AAAA."

        if data_obj.date() > datetime.now().date():
            return False, "R6: Não é permitido registrar notas ou frequências com datas futuras em relação à data atual do servidor."

        return True, data_obj.strftime("%Y-%m-%d")

    def _lancar(self):
        try:
            mat_id = int(self.entry_mat.get().strip())
        except ValueError:
            messagebox.showwarning("Atenção", "ID Matrícula deve ser um número inteiro.")
            return

        # REGRA 1: Validação de Notas (0 a 10)
        try:
            nota_raw = self.entry_nota.get().replace(",", ".").strip()
            valor_nota = float(nota_raw)
        except ValueError:
            messagebox.showerror("Erro de Validação", "R1: A nota deve ser um número válido entre 0.0 e 10.0.")
            return

        if valor_nota < 0.0 or valor_nota > 10.0:
            messagebox.showerror("Erro de Validação", "R1: A nota deve estar entre 0.0 e 10.0 (Validação de Notas).")
            return

        # REGRA 6: Consistência Temporal (bloqueia datas futuras)
        data_str = self.entry_data.get().strip() or datetime.now().strftime("%Y-%m-%d")
        valida_dt, res_dt = self._validar_data_input(data_str)
        if not valida_dt:
            messagebox.showerror("Erro de Validação", res_dt)
            return

        dados = {
            "matricula_turma_id": mat_id,
            "valor_nota":         valor_nota,
            "data_registro":      res_dt
        }

        resp, status = api.lancar_avaliacao(dados)
        if status == 201:
            risco = resp.get("risco_nota_atualizado", False)
            msg = resp.get("mensagem", "Nota lançada com sucesso!")
            if risco:
                msg += "\n⚠ R5: Aluno classificado com Risco de Reprovação por Nota (média parcial < 5.0)!"
            messagebox.showinfo("Sucesso", msg)
            self._limpar()
            self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao lançar nota."))

    def _atualizar(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma avaliação na tabela.")
            return

        # REGRA 1: Validação de Notas (0 a 10)
        try:
            nota_raw = self.entry_nota.get().replace(",", ".").strip()
            valor_nota = float(nota_raw)
        except ValueError:
            messagebox.showerror("Erro de Validação", "R1: A nota deve ser um número válido entre 0.0 e 10.0.")
            return

        if valor_nota < 0.0 or valor_nota > 10.0:
            messagebox.showerror("Erro de Validação", "R1: A nota deve estar entre 0.0 e 10.0 (Validação de Notas).")
            return

        # REGRA 6: Consistência Temporal (bloqueia datas futuras)
        data_str = self.entry_data.get().strip() or datetime.now().strftime("%Y-%m-%d")
        valida_dt, res_dt = self._validar_data_input(data_str)
        if not valida_dt:
            messagebox.showerror("Erro de Validação", res_dt)
            return

        dados = {
            "valor_nota":    valor_nota,
            "data_registro": res_dt
        }

        resp, status = api.atualizar_avaliacao(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Avaliação atualizada com sucesso!"))
            self._limpar()
            self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao atualizar."))

    def _remover(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma avaliação na tabela.")
            return
        id_para_remover = self._id_selecionado
        if not messagebox.askyesno("Confirmar", "Deseja remover esta avaliação?"):
            return
        resp, status = api.deletar_avaliacao(id_para_remover)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Avaliação removida com sucesso."))
            self._limpar()
            self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao remover."))

    def _limpar(self):
        self.entry_mat.delete(0, tk.END)
        self.entry_nota.delete(0, tk.END)
        self.entry_data.delete(0, tk.END); self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        if hasattr(self, "combo_disciplina"):
            self.combo_disciplina.set("Todas")
            self.disciplina_filtro = "Todas"
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

    def _construir_mapeamento_disciplina(self):
        """Constrói dicionário matricula_turma_id -> nome da disciplina."""
        try:
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
                mapa[str(m["id"])] = nome
            return mapa
        except Exception:
            return {}

    def _criar_filtro_disciplina(self):
        """Cria dropdown para filtrar avaliações por disciplina."""
        if hasattr(self, "combo_disciplina"):
            return
            
        frame_filtro = tk.Frame(self, bg="#f0f0f0")
        frame_filtro.pack(fill=tk.X, padx=15, pady=4)
        tk.Label(frame_filtro, text="Filtrar por Disciplina:", bg="#f0f0f0", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
        disciplinas = api.listar_disciplinas()
        nomes = ["Todas"] + [d["nome"] for d in disciplinas]
        self.combo_disciplina = ttk.Combobox(frame_filtro, values=nomes, state="readonly", width=25)
        self.combo_disciplina.current(0)
        self.combo_disciplina.pack(side=tk.LEFT, padx=5)
        self.combo_disciplina.bind("<<ComboboxSelected>>", self._aplicar_filtro_disciplina)
        self.disciplina_filtro = "Todas"

    def _aplicar_filtro_disciplina(self, event=None):
        """Aplica o filtro selecionado e recarrega a lista."""
        self.disciplina_filtro = self.combo_disciplina.get()
        self._limpar()
        self._carregar()
