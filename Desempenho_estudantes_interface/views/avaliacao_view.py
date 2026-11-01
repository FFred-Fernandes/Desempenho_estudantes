# PARTE 4: Tela de lançamento de Avaliações usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
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
        self.entry_mat = tk.Entry(frame_form, width=12)
        self.entry_mat.grid(row=0, column=1, padx=8)

        tk.Label(frame_form, text="Nota (0 a 10):", bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.entry_nota = tk.Entry(frame_form, width=12)
        self.entry_nota.grid(row=0, column=3, padx=8)

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Lançar Nota",    "#27ae60", self._lancar),
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

        colunas = ("id", "matricula_turma_id", "valor_nota", "data_registro")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=14)

        headers = {
            "id": ("ID", 50), "matricula_turma_id": ("ID Matrícula", 120),
            "valor_nota": ("Nota", 80), "data_registro": ("Data de Registro", 200)
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
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for a in api.listar_avaliacoes():
            # Condição para colorir nota abaixo de 5 em vermelho
            nota = float(a["valor_nota"])
            tag = "nota_baixa" if nota < 5.0 else "nota_ok"
            self.tabela.insert("", tk.END,
                               values=(a["id"], a["matricula_turma_id"],
                                       f'{nota:.1f}', a["data_registro"]),
                               tags=(tag,))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_mat.delete(0, tk.END);  self.entry_mat.insert(0, v[1])
        self.entry_nota.delete(0, tk.END); self.entry_nota.insert(0, v[2])
        self._id_selecionado = v[0]

    def _lancar(self):
        try:
            dados = {
                "matricula_turma_id": int(self.entry_mat.get()),
                "valor_nota":         float(self.entry_nota.get())
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
            messagebox.showerror("Erro", resp.get("erro", "Erro ao lançar nota."))

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
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

