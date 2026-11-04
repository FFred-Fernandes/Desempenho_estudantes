# PARTE 4: Tela de Análise Estatística (Anomalia + Fechamento) usando Tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api

class AnaliseView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self._construir_tela()

    def _construir_tela(self):
        tk.Label(self, text="📊  Análise de Desempenho da Turma",
                 font=("Helvetica", 16, "bold"),
                 bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)

        # ── Entrada do ID de turma ───────────────────────────
        frame_id = tk.Frame(self, bg="#f0f0f0")
        frame_id.pack(pady=20)

        tk.Label(frame_id, text="ID da Turma:", font=("Helvetica", 12),
                 bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.entry_turma_id = tk.Entry(frame_id, width=10, font=("Helvetica", 12))
        self.entry_turma_id.pack(side=tk.LEFT, padx=5)

        # ── Botões de análise ────────────────────────────────
        frame_btns = tk.Frame(self, bg="#f0f0f0")
        frame_btns.pack(pady=10)

        tk.Button(frame_btns,
                  text="🔍  Verificar Anomalia (Regra 7)",
                  bg="#8e44ad", fg="white",
                  font=("Helvetica", 10, "bold"),
                  width=32, cursor="hand2",
                  command=self._verificar_anomalia
                  ).pack(pady=6)

        tk.Button(frame_btns,
                  text="🔒  Fechar Semestre (Regra 9)",
                  bg="#c0392b", fg="white",
                  font=("Helvetica", 10, "bold"),
                  width=32, cursor="hand2",
                  command=self._fechar_semestre
                  ).pack(pady=6)

        # ── Área de resultado ────────────────────────────────
        frame_res = tk.LabelFrame(self, text="Resultado da Análise",
                                  bg="#f0f0f0", font=("Helvetica", 10, "bold"),
                                  padx=15, pady=15)
        frame_res.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.texto_resultado = tk.Text(
            frame_res, height=18, state="disabled",
            font=("Courier", 10), bg="#1e1e2e", fg="#cdd6f4",
            relief=tk.FLAT, padx=10, pady=10
        )
        self.texto_resultado.pack(fill=tk.BOTH, expand=True)

    def _get_turma_id(self):
        try:
            return int(self.entry_turma_id.get().strip())
        except ValueError:
            messagebox.showwarning("Atenção", "Digite um ID de turma válido (número inteiro).")
            return None

    def _exibir_resultado(self, dados):
        # Formata e exibe o dicionário de resposta da API na área de texto
        self.texto_resultado.config(state="normal")
        self.texto_resultado.delete("1.0", tk.END)
        for chave, valor in dados.items():
            self.texto_resultado.insert(tk.END, f"  {chave:<30}: {valor}\n")
        self.texto_resultado.config(state="disabled")

    def _verificar_anomalia(self):
        # REGRA 7: Detecção de Anomalia de Turma
        turma_id = self._get_turma_id()
        if turma_id is None:
            return
        resp, status = api.verificar_anomalia(turma_id)
        self._exibir_resultado(resp)

        if status == 200 and resp.get("alerta_anomalia"):
            messagebox.showwarning(
                "⚠ R7: ANOMALIA DETECTADA",
                f"R7: A média da turma {turma_id} está abaixo de 30%!\n"
                f"Média apurada: {resp.get('media_turma', 'N/A')}\n"
                "Possível anomalia na dificuldade da prova ou ensino."
            )
        elif status == 200:
            messagebox.showinfo(
                "Análise Concluída",
                resp.get("mensagem", "Desempenho da turma dentro da normalidade.")
            )
        else:
            messagebox.showerror("Erro na Análise", resp.get("erro", "Erro ao verificar anomalia."))

    def _fechar_semestre(self):
        # REGRA 9: Pré-requisito de Análise Final
        turma_id = self._get_turma_id()
        if turma_id is None:
            return
        if not messagebox.askyesno("Confirmar Fechamento", f"Deseja fechar o semestre da Turma {turma_id}?\nEsta ação exigirá 100% das notas lançadas para alunos ativos (Regra 9)."):
            return
        resp, status = api.fechar_semestre(turma_id)
        self._exibir_resultado(resp)

        if status == 200:
            messagebox.showinfo("Semestre Fechado", resp.get("mensagem", "Fechamento concluído com sucesso!"))
        else:
            messagebox.showerror("R9: Fechamento Bloqueado", resp.get("erro", "Erro no fechamento do semestre."))
