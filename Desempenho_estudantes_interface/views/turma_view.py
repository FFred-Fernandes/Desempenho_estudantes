# PARTE 4: Tela de gerenciamento de Turmas usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api

class TurmaView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self._construir_tela()

    def _construir_tela(self):
        tk.Label(self, text="🏫  Gerenciamento de Turmas",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)

        # ── Formulário ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Dados da Turma",
                                   bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                   padx=10, pady=8)
        frame_form.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(frame_form, text="ID Disciplina:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_disc_id = tk.Entry(frame_form, width=10)
        self.entry_disc_id.grid(row=0, column=1, padx=8)

        tk.Label(frame_form, text="Semestre (1/2):", bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.combo_semestre = ttk.Combobox(frame_form, width=12, values=["1", "2"], state="readonly")
        self.combo_semestre.set("1")
        self.combo_semestre.grid(row=0, column=3, padx=8)

        tk.Label(frame_form, text="Ano:", bg="#f0f0f0").grid(row=0, column=4, sticky="w")
        self.entry_ano = tk.Entry(frame_form, width=10)
        self.entry_ano.grid(row=0, column=5, padx=8)

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Cadastrar",   "#27ae60", self._cadastrar),
            ("🗑️   Excluir",     "#e74c3c", self._excluir),
            ("🔄  Atualizar Lista", "#7f8c8d", self._carregar),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"), width=16, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=5)

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        # Mapping of disciplina_id to nome
        self._disc_map = self._construir_mapeamento_disciplina()
        colunas = ("id", "disciplina_id", "disciplina", "semestre", "ano")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=14)

        headers = {"id": ("ID Turma", 80), "disciplina_id": ("ID Disciplina", 120),
                   "disciplina": ("Disciplina", 150), "semestre": ("Semestre", 120), "ano": ("Ano", 80)}
        for col, (label, w) in headers.items():
            self.tabela.heading(col, text=label)
            self.tabela.column(col, width=w, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_linha)

        self._carregar()

    def _carregar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for t in api.listar_turmas():
            disciplina_nome = self._disc_map.get(t["disciplina_id"], "")
            self.tabela.insert("", tk.END,
                               values=(t["id"], t["disciplina_id"], disciplina_nome, t["semestre"], t["ano"]))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_disc_id.delete(0, tk.END);  self.entry_disc_id.insert(0, v[1])
        if v[2] in ["1", "2"]:
            self.combo_semestre.set(v[2])
        self.entry_ano.delete(0, tk.END);      self.entry_ano.insert(0, v[3])
        self._id_selecionado = v[0]

    def _cadastrar(self):
        try:
            dados = {
                "disciplina_id": int(self.entry_disc_id.get()),
                "semestre":      self.combo_semestre.get().strip(),
                "ano":           int(self.entry_ano.get())
            }
        except ValueError:
            messagebox.showwarning("Atenção", "ID Disciplina e Ano devem ser números inteiros.")
            return
        resp, status = api.cadastrar_turma(dados)
        if status == 201:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao cadastrar turma."))

    def _excluir(self):
        # existing code unchanged
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma turma na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta turma?"):
            return
        resp, status = api.deletar_turma(self._id_selecionado)
        if status == 200:
            # unchanged
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao excluir."))

    def _limpar(self):
        self.entry_disc_id.delete(0, tk.END)
        self.entry_semestre.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        # disciplina name not editable directly
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

    def _construir_mapeamento_disciplina(self):
        """Constrói dicionário disciplina_id → nome da disciplina."""
        disciplinas = api.listar_disciplinas()
        return {d["id"]: d["nome"] for d in disciplinas}
