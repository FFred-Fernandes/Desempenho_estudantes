# PARTE 4: Tela de gerenciamento de Matrículas usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api

class MatriculaView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
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

        # ── Botões ──────────────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=5)

        botoes = [
            ("➕  Matricular",        "#27ae60", self._matricular),
            ("📊  Atualizar Frequência","#2980b9", self._atualizar_freq),
            ("🗑️   Remover",           "#e74c3c", self._remover),
            ("🔄  Atualizar Lista",    "#7f8c8d", self._carregar),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"), width=18, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=4)

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        colunas = ("id", "estudante_id", "turma_id", "frequencia_percentual", "risco_falta", "risco_nota")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=13)

        headers = {
            "id": ("ID", 50), "estudante_id": ("ID Estudante", 110),
            "turma_id": ("ID Turma", 80),
            "frequencia_percentual": ("Frequência %", 100),
            "risco_falta": ("⚠ Risco Falta", 110),
            "risco_nota":  ("⚠ Risco Nota", 100)
        }
        for col, (label, w) in headers.items():
            self.tabela.heading(col, text=label)
            self.tabela.column(col, width=w, anchor="center")

        # Tag de cor para matrículas em risco
        self.tabela.tag_configure("risco", background="#ffe0e0")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_linha)

        self._carregar()

    def _carregar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for m in api.listar_matriculas():
            # Condição para destacar em vermelho matrículas com risco
            tag = "risco" if m["risco_falta"] or m["risco_nota"] else ""
            self.tabela.insert("", tk.END,
                               values=(m["id"], m["estudante_id"], m["turma_id"],
                                       f'{m["frequencia_percentual"]:.1f}%',
                                       "⚠ SIM" if m["risco_falta"] else "NÃO",
                                       "⚠ SIM" if m["risco_nota"]  else "NÃO"),
                               tags=(tag,))

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        self.entry_est.delete(0, tk.END);   self.entry_est.insert(0, v[1])
        self.entry_turma.delete(0, tk.END); self.entry_turma.insert(0, v[2])
        freq_str = v[3].replace("%", "")
        self.entry_freq.delete(0, tk.END);  self.entry_freq.insert(0, freq_str)
        self._id_selecionado = v[0]

    def _matricular(self):
        try:
            dados = {
                "estudante_id": int(self.entry_est.get()),
                "turma_id":     int(self.entry_turma.get())
            }
        except ValueError:
            messagebox.showwarning("Atenção", "IDs devem ser números inteiros.")
            return
        resp, status = api.realizar_matricula(dados)
        if status == 201:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao matricular."))

    def _atualizar_freq(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma matrícula na tabela.")
            return
        try:
            dados = {"frequencia_percentual": float(self.entry_freq.get())}
        except ValueError:
            messagebox.showwarning("Atenção", "Frequência deve ser um número válido.")
            return
        resp, status = api.atualizar_frequencia(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem", "Dados da matrícula atualizados com sucesso!"))
            self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao atualizar frequência."))

    def _remover(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione uma matrícula na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja remover esta matrícula?"):
            return
        resp, status = api.deletar_matricula(self._id_selecionado)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao remover."))

    def _limpar(self):
        self.entry_est.delete(0, tk.END)
        self.entry_turma.delete(0, tk.END)
        self.entry_freq.delete(0, tk.END); self.entry_freq.insert(0, "100.0")
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado

