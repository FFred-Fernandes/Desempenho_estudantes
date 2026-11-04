# PARTE 4: Tela de gerenciamento de Matrículas usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import api_client as api

class MatriculaView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self._disc_map = {}
        self._construir_tela()

    def _construir_tela(self):
        tk.Label(self, text="📋  Gerenciamento de Matrículas",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)

        # ── Formulário ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Dados da Matrícula",
                                   bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                   padx=10, pady=8)
        frame_form.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(frame_form, text="ID Estudante:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_est = tk.Entry(frame_form, width=12)
        self.entry_est.grid(row=0, column=1, padx=8)

        tk.Label(frame_form, text="ID Turma:", bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.entry_turma = tk.Entry(frame_form, width=12)
        self.entry_turma.grid(row=0, column=3, padx=8)

        tk.Label(frame_form, text="Frequência (%):", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_freq = tk.Entry(frame_form, width=12)
        self.entry_freq.insert(0, "100.0")
        self.entry_freq.grid(row=1, column=1, padx=8)

        # REGRA 6: Consistência Temporal (permite datas anteriores/atuais, bloqueia datas futuras)
        tk.Label(frame_form, text="Data (AAAA-MM-DD):", bg="#f0f0f0").grid(row=1, column=2, sticky="w", pady=3)
        self.entry_data = tk.Entry(frame_form, width=14)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=1, column=3, padx=8)

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Matricular",          "#27ae60", self._matricular),
            ("📊  Atualizar Frequência", "#2980b9", self._atualizar_freq),
            ("🗑️   Remover",             "#e74c3c", self._remover),
            ("🔄  Atualizar Lista",      "#7f8c8d", self._carregar),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"), width=18, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=4)

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        colunas = ("id", "estudante_id", "turma_id", "disciplina", "frequencia_percentual", "risco_falta", "risco_nota", "data_registro")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=13)

        headers = {
            "id": ("ID", 45),
            "estudante_id": ("ID Estudante", 95),
            "turma_id": ("ID Turma", 75),
            "disciplina": ("Disciplina", 160),
            "frequencia_percentual": ("Frequência %", 95),
            "risco_falta": ("⚠ Risco Falta (R4)", 110),
            "risco_nota":  ("⚠ Risco Nota (R5)", 110),
            "data_registro": ("Data Registro (R6)", 180)
        }
        for col, (label, w) in headers.items():
            self.tabela.heading(col, text=label)
            self.tabela.column(col, width=w, anchor="center")

        # Tag de cor para matrículas em risco (R4 ou R5)
        self.tabela.tag_configure("risco", background="#ffe0e0")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_linha)

        self._carregar()

    def _carregar(self):
        # Atualiza o mapa de disciplinas a cada recarga
        self._disc_map = self._construir_mapeamento_disciplina()

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for m in api.listar_matriculas():
            tag = "risco" if m.get("risco_falta") or m.get("risco_nota") else ""
            data_reg = m.get("data_registro", "")
            t_id = m.get("turma_id")
            disciplina_nome = self._disc_map.get(t_id) or self._disc_map.get(str(t_id)) or ""
            freq_val = float(m.get("frequencia_percentual", 100.0))

            self.tabela.insert("", tk.END,
                               values=(m.get("id"), m.get("estudante_id"), t_id, disciplina_nome,
                                       f'{freq_val:.1f}%',
                                       "⚠ SIM" if m.get("risco_falta") else "NÃO",
                                       "⚠ SIM" if m.get("risco_nota")  else "NÃO",
                                       data_reg),
                               tags=(tag,))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_est.delete(0, tk.END);   self.entry_est.insert(0, v[1])
        self.entry_turma.delete(0, tk.END); self.entry_turma.insert(0, v[2])
        freq_str = str(v[4]).replace("%", "").strip()
        self.entry_freq.delete(0, tk.END);  self.entry_freq.insert(0, freq_str)
        if len(v) > 7 and v[7]:
            self.entry_data.delete(0, tk.END); self.entry_data.insert(0, v[7].split()[0])
        self._id_selecionado = v[0]

    def _validar_data_input(self, data_str):
        """Valida formato de data e bloqueia datas futuras (R6)."""
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

        # REGRA 6: Bloqueia datas futuras em relação a hoje
        if data_obj.date() > datetime.now().date():
            return False, "R6: Não é permitido registrar notas ou frequências com datas futuras em relação à data atual do servidor."

        return True, data_obj.strftime("%Y-%m-%d")

    def _matricular(self):
        # 1. Validar IDs
        try:
            est_id = int(self.entry_est.get().strip())
            turma_id = int(self.entry_turma.get().strip())
        except ValueError:
            messagebox.showwarning("Atenção", "ID Estudante e ID Turma devem ser números inteiros.")
            return

        # 2. Validar Frequência (REGRA 2)
        try:
            freq_raw = self.entry_freq.get().replace("%", "").replace(",", ".").strip()
            if not freq_raw:
                messagebox.showwarning("Atenção", "Informe o percentual de frequência.")
                return
            freq_digitada = float(freq_raw)
        except ValueError:
            messagebox.showerror("Erro de Validação", "R2: A frequência deve ser um número válido entre 0% e 100%.")
            return

        if freq_digitada < 0.0 or freq_digitada > 100.0:
            messagebox.showerror("Erro de Validação", "R2: A frequência não pode ser inferior a 0% nem superior a 100%.")
            return

        # 3. Validar Data (REGRA 6)
        data_str = self.entry_data.get().strip() or datetime.now().strftime("%Y-%m-%d")
        valida_dt, res_dt = self._validar_data_input(data_str)
        if not valida_dt:
            messagebox.showerror("Erro de Validação", res_dt)
            return

        dados = {
            "estudante_id":          est_id,
            "turma_id":              turma_id,
            "frequencia_percentual": freq_digitada,
            "data_registro":         res_dt
        }

        resp, status = api.realizar_matricula(dados)
        if status == 201:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Matrícula realizada com sucesso!"))
            self._limpar()
            self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao matricular."))

    def _atualizar_freq(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma matrícula na tabela para atualizar a frequência.")
            return

        # 1. Validar Frequência (REGRA 2)
        try:
            freq_raw = self.entry_freq.get().replace("%", "").replace(",", ".").strip()
            if not freq_raw:
                messagebox.showwarning("Atenção", "Informe o percentual de frequência.")
                return
            freq_digitada = float(freq_raw)
        except ValueError:
            messagebox.showerror("Erro de Validação", "R2: A frequência deve ser um número válido entre 0% e 100%.")
            return

        if freq_digitada < 0.0 or freq_digitada > 100.0:
            messagebox.showerror("Erro de Validação", "R2: A frequência não pode ser inferior a 0% nem superior a 100%.")
            return

        # 2. Validar Data (REGRA 6)
        data_str = self.entry_data.get().strip() or datetime.now().strftime("%Y-%m-%d")
        valida_dt, res_dt = self._validar_data_input(data_str)
        if not valida_dt:
            messagebox.showerror("Erro de Validação", res_dt)
            return

        dados = {
            "frequencia_percentual": freq_digitada,
            "data_registro":         res_dt
        }

        resp, status = api.atualizar_frequencia(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Dados da matrícula atualizados com sucesso!"))
            self._carregar()
        else:
            messagebox.showerror("Erro de Validação", resp.get("erro", "Erro ao atualizar frequência."))

    def _remover(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma matrícula na tabela.")
            return
        id_para_remover = self._id_selecionado
        if not messagebox.askyesno("Confirmar", "Deseja remover esta matrícula?"):
            return
        resp, status = api.deletar_matricula(id_para_remover)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Matrícula deletada com sucesso."))
            self._limpar()
            self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao remover."))

    def _limpar(self):
        self.entry_est.delete(0, tk.END)
        self.entry_turma.delete(0, tk.END)
        self.entry_freq.delete(0, tk.END); self.entry_freq.insert(0, "100.0")
        self.entry_data.delete(0, tk.END); self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

    def _construir_mapeamento_disciplina(self):
        """Constrói dicionário turma_id -> nome da disciplina garantindo chaves int e str."""
        try:
            turmas = api.listar_turmas()
            disciplinas = api.listar_disciplinas()
            disc_id_to_nome = {}
            for d in disciplinas:
                disc_id_to_nome[d["id"]] = d["nome"]
                disc_id_to_nome[str(d["id"])] = d["nome"]

            mapa = {}
            for t in turmas:
                t_id = t["id"]
                nome = t.get("disciplina_nome") or disc_id_to_nome.get(t.get("disciplina_id")) or disc_id_to_nome.get(str(t.get("disciplina_id"))) or ""
                mapa[t_id] = nome
                mapa[str(t_id)] = nome
            return mapa
        except Exception:
            return {}
