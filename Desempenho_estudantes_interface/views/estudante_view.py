# PARTE 4: Tela de gerenciamento de Estudantes usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api

class EstudanteView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self.filtro_ativo = tk.StringVar(value="Todos")
        self._lista_estudantes_cache = []
        self._construir_tela()

    def _construir_tela(self):
        # ── Título ──────────────────────────────────────────
        tk.Label(self, text="👩‍🎓  Gerenciamento de Estudantes",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white",
                 pady=10).pack(fill=tk.X)

        # ── Formulário ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Dados do Estudante",
                                   bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                   padx=10, pady=8)
        frame_form.pack(fill=tk.X, padx=15, pady=8)

        # Linha 1: Nome e CPF
        tk.Label(frame_form, text="Nome:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=1, padx=8, pady=3)

        tk.Label(frame_form, text="CPF:", bg="#f0f0f0").grid(row=0, column=2, sticky="w", pady=3)
        self.entry_cpf = tk.Entry(frame_form, width=20)
        self.entry_cpf.grid(row=0, column=3, padx=8, pady=3)

        # Linha 2: Matrícula e Status
        tk.Label(frame_form, text="Matrícula:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_matricula = tk.Entry(frame_form, width=30)
        self.entry_matricula.grid(row=1, column=1, padx=8, pady=3)

        tk.Label(frame_form, text="Status:", bg="#f0f0f0").grid(row=1, column=2, sticky="w", pady=3)
        self.combo_status = ttk.Combobox(frame_form, width=17,
                                          values=["Ativo", "Trancado", "Evasão"],
                                          state="readonly")
        self.combo_status.set("Ativo")
        self.combo_status.grid(row=1, column=3, padx=8, pady=3)

        # ── Botões de Ação ──────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=4)

        botoes = [
            ("➕  Cadastrar",   "#27ae60", self._cadastrar),
            ("✏️   Atualizar",   "#2980b9", self._atualizar),
            ("🗑️   Inativar",    "#e74c3c", self._inativar),
            ("🔄  Atualizar Lista", "#7f8c8d", self._carregar_da_api),
        ]
        for texto, cor, cmd in botoes:
            tk.Button(frame_btns, text=texto, bg=cor, fg="white",
                      font=("Helvetica", 9, "bold"),
                      width=16, cursor="hand2", command=cmd
                      ).pack(side=tk.LEFT, padx=5)

        # ── Barra de Filtragem (Todos | Ativos | Inativos) ───
        frame_filtro = tk.Frame(self, bg="#e2e8f0", padx=10, pady=5)
        frame_filtro.pack(fill=tk.X, padx=15, pady=4)

        tk.Label(frame_filtro, text="Filtrar:",
                 font=("Helvetica", 9, "bold"), bg="#e2e8f0", fg="#334155").pack(side=tk.LEFT, padx=6)

        opcoes_filtro = [("Todos", "Todos"), ("Apenas Ativos", "Ativos"), ("Apenas Inativos", "Inativos")]
        for texto, valor in opcoes_filtro:
            tk.Radiobutton(frame_filtro, text=texto, value=valor, variable=self.filtro_ativo,
                           bg="#e2e8f0", activebackground="#e2e8f0",
                           font=("Helvetica", 9), command=self._aplicar_filtro_tabela).pack(side=tk.LEFT, padx=10)

        # ── Tabela ──────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg="#f0f0f0")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=6)

        colunas = ("id", "nome", "cpf", "matricula", "status", "ativo")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=13)

        headers = {
            "id": ("ID", 45),
            "nome": ("Nome", 200),
            "cpf": ("CPF", 120),
            "matricula": ("Matrícula", 120),
            "status": ("Status Acadêmico", 110),
            "ativo": ("Situação no Sistema", 120)
        }
        for col, (label, w) in headers.items():
            self.tabela.heading(col, text=label)
            self.tabela.column(col, width=w, anchor="center")

        # Configurações de cores:
        # - Aluno inativo no sistema: Vermelho
        # - Aluno ativo no sistema com status Trancado/Evasão: Cinza
        # - Aluno ativo no sistema com status Ativo: Verde
        self.tabela.tag_configure("aluno_inativo", background="#fee2e2", foreground="#7f1d1d")
        self.tabela.tag_configure("aluno_afastado", background="#e2e8f0", foreground="#334155")
        self.tabela.tag_configure("aluno_ativo", background="#dcfce7", foreground="#14532d")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_linha)

        self._carregar_da_api()

    def _carregar_da_api(self):
        # Busca da API apenas quando abre a tela ou clica em Atualizar Lista
        self._lista_estudantes_cache = api.listar_estudantes()
        self._aplicar_filtro_tabela()

    def _aplicar_filtro_tabela(self):
        # Filtragem instantânea na memória (sem chamar a rede)
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        filtro = self.filtro_ativo.get()
        for e in self._lista_estudantes_cache:
            esta_ativo = e.get("ativo", True)
            status_acad = e.get("status", "Ativo")
            
            # Filtro condicional: Todos | Apenas Ativos | Apenas Inativos
            if filtro == "Ativos" and not esta_ativo:
                continue
            if filtro == "Inativos" and esta_ativo:
                continue

            situacao_texto = "Ativo" if esta_ativo else "Inativo"

            # Definição de cores:
            # 1. Inativo no sistema -> Vermelho
            # 2. Ativo no sistema mas Trancado ou Evasão -> Cinza
            # 3. Ativo cursando -> Verde
            if not esta_ativo:
                tag_cor = "aluno_inativo"
            elif status_acad in ["Trancado", "Evasão"]:
                tag_cor = "aluno_afastado"
            else:
                tag_cor = "aluno_ativo"

            self.tabela.insert(
                "",
                tk.END,
                values=(
                    e["id"],
                    e["nome"],
                    e["cpf"],
                    e["matricula"],
                    status_acad,
                    situacao_texto
                ),
                tags=(tag_cor,)
            )

    def _selecionar_linha(self, _event):
        sel = self.tabela.selection()
        if not sel:
            return
        valores = self.tabela.item(sel[0], "values")
        self.entry_nome.delete(0, tk.END);      self.entry_nome.insert(0, valores[1])
        self.entry_cpf.delete(0, tk.END);       self.entry_cpf.insert(0, valores[2])
        self.entry_matricula.delete(0, tk.END); self.entry_matricula.insert(0, valores[3])
        self.combo_status.set(valores[4])
        self._id_selecionado = valores[0]

    def _cadastrar(self):
        dados = {
            "nome":      self.entry_nome.get().strip(),
            "cpf":       self.entry_cpf.get().strip(),
            "matricula": self.entry_matricula.get().strip()
        }
        if not all(dados.values()):
            messagebox.showwarning("Atenção", "Preencha Nome, CPF e Matrícula.")
            return
        resp, status = api.cadastrar_estudante(dados)
        if status == 201:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar_da_api()
        else:
            # Analisar mensagem de erro para identificar duplicidade
            erro_msg = resp.get("erro", "Erro ao cadastrar.").lower()
            if "matricula" in erro_msg:
                messagebox.showerror("Erro", "Matrícula já cadastrada.")
            elif "cpf" in erro_msg:
                messagebox.showerror("Erro", "CPF já cadastrado.")
            else:
                messagebox.showerror("Erro", resp.get("erro", "Erro ao cadastrar."))

    def _atualizar(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione um estudante na tabela.")
            return
        dados = {"nome": self.entry_nome.get().strip(), "status": self.combo_status.get()}
        resp, status = api.atualizar_estudante(self._id_selecionado, dados)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar_da_api()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao atualizar."))

    def _inativar(self):
        if not hasattr(self, "_id_selecionado"):
            messagebox.showwarning("Atenção", "Selecione um estudante na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja inativar este estudante? (Exclusão lógica - Regra 8)"):
            return
        resp, status = api.deletar_estudante(self._id_selecionado)
        if status == 200:
            messagebox.showinfo("Sucesso", resp.get("mensagem"))
            self._limpar(); self._carregar_da_api()
        else:
            messagebox.showerror("Erro", resp.get("erro", "Erro ao inativar."))

    def _limpar(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_matricula.delete(0, tk.END)
        self.combo_status.set("Ativo")
        if hasattr(self, "_id_selecionado"):
            del self._id_selecionado
