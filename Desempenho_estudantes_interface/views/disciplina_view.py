# PARTE 4: Tela de gerenciamento de Disciplinas usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api

class DisciplinaView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self._construir_tela()

    def _construir_tela(self):
        tk.Label(self, text="📚  Gerenciamento de Disciplinas",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)

        # ── Formulário ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Dados da Disciplina",
                                   bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                   padx=10, pady=8)
        frame_form.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(frame_form, text="Código:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_codigo = tk.Entry(frame_form, width=20)
        self.entry_codigo.grid(row=0, column=1, padx=8)

        tk.Label(frame_form, text="Nome:", bg="#f0f0f0").grid(row=0, column=2, sticky="w", pady=3)
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=3, padx=8)

        tk.Label(frame_form, text="Avaliações obrigatórias:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_avals = tk.Entry(frame_form, width=10)
        self.entry_avals.insert(0, "3")
        self.entry_avals.grid(row=1, column=1, padx=8)

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Cadastrar",   "#27ae60", self._cadastrar),
            ("✏️   Atualizar",   "#2980b9", self._atualizar),
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

        colunas = ("id", "codigo", "nome", "avaliacoes_obrigatorias")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=14)

        headers = {"id": ("ID", 50), "codigo": ("Código", 100),
                   "nome": ("Nome", 280), "avaliacoes_obrigatorias": ("Avals. Obrigatórias", 150)}
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
        for d in api.listar_disciplinas():
            self.tabela.insert("", tk.END,
                               values=(d["id"], d["codigo"], d["nome"], d["avaliacoes_obrigatorias"]))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_codigo.delete(0, tk.END); self.entry_codigo.insert(0, v[1])
        self.entry_nome.delete(0, tk.END);   self.entry_nome.insert(0, v[2])
        self.entry_avals.delete(0, tk.END);  self.entry_avals.insert(0, v[3])
        self._id_selecionado = v[0]

    def _cadastrar(self):
        dados = {
            "codigo": self.entry_codigo.get().strip(),
            "nome":   self.entry_nome.get().strip(),
            "total_avaliacoes_obrigatorias": int(self.entry_avals.get() or 3)
        }
        if not dados["codigo"] or not dados["nome"]:
            messagebox.showwarning("Atenção", "Preencha Código e Nome.")
            return
        resp, status = api.cadastrar_disciplina(dados)
        if status == 201:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao cadastrar."))

    def _atualizar(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma disciplina na tabela.")
            return
        dados = {
            "nome": self.entry_nome.get().strip(),
            "total_avaliacoes_obrigatorias": int(self.entry_avals.get() or 3)
        }
        resp, status = api.atualizar_disciplina(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao atualizar."))

    def _excluir(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma disciplina na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta disciplina?"):
            return
        resp, status = api.deletar_disciplina(self._id_selecionado)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao excluir."))

    def _limpar(self):
        self.entry_codigo.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)
        self.entry_avals.delete(0, tk.END); self.entry_avals.insert(0, "3")
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

