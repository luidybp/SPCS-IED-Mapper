# ==============================================================================
# MÓDULO 2: INTERFACE GRÁFICA E CONSOLIDADOR DE I/O (interface.py)
# Responsável pelas janelas, estilos visuais, agrupamento e exportação CSV.
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# Importa o dicionário de funções do módulo funcoes_ansi.py
from funcoes_ansi import ANSI_DATABASE


class SPCSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPCS IED Mapper — Mapeamento de EAs, BIs e BOs (Build 3.0)")
        self.geometry("1240x760")
        self.minsize(1000, 640)
        self.configure(bg="#1e1e2e")

        self._configurar_estilo()
        self.checkbox_vars = {}

        # Barra de Cabeçalho Superior
        frame_header_top = ttk.Frame(self)
        frame_header_top.pack(fill=tk.X, padx=14, pady=(10, 0))
        ttk.Label(
            frame_header_top,
            text="⚡ SPCS IED Mapper",
            style="Header.TLabel"
        ).pack(side=tk.LEFT)
        ttk.Label(
            frame_header_top,
            text="Build 3.0 — 23/10/2026",
            style="Build.TLabel"
        ).pack(side=tk.RIGHT)

        # Abas Principais
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.tab_consulta = ttk.Frame(self.notebook)
        self.tab_workstatement = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_consulta, text="  [1] Consulta por Função ANSI  ")
        self.notebook.add(self.tab_workstatement, text="  [2] Consolidador de Workstatement (Lista de I/O Agrupada)  ")

        self._construir_aba_consulta()
        self._construir_aba_workstatement()

        # Barra de Rodapé Fixa (Status Bar)
        frame_footer = tk.Frame(self, bg="#181825", height=28)
        frame_footer.pack(fill=tk.X, side=tk.BOTTOM)
        lbl_footer_esq = tk.Label(
            frame_footer,
            text="  SPCS IED Mapper | Build 3.0 (23/10/2026)",
            bg="#181825",
            fg="#a6adc8",
            font=("Segoe UI", 9)
        )
        lbl_footer_esq.pack(side=tk.LEFT, pady=4)
        lbl_footer_dir = tk.Label(
            frame_footer,
            text="Desenvolvido por Luidy Bueno Paviani  ",
            bg="#181825",
            fg="#8be9fd",
            font=("Segoe UI", 9, "bold")
        )
        lbl_footer_dir.pack(side=tk.RIGHT, pady=4)

    def _configurar_estilo(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        bg_dark = "#1e1e2e"
        bg_panel = "#282a36"
        fg_text = "#f8f8f2"
        accent = "#4a90e2"

        style.configure("TFrame", background=bg_dark)
        style.configure("Panel.TFrame", background=bg_panel)
        style.configure("TLabel", background=bg_dark, foreground=fg_text, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=bg_dark, foreground="#8be9fd", font=("Segoe UI", 12, "bold"))
        style.configure("Build.TLabel", background=bg_dark, foreground="#f1fa8c", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook", background=bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background="#343746", foreground=fg_text, padding=[12, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "#ffffff")])
        style.configure("Accent.TButton", background=accent, foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("active", "#357abd")])

        # Estilo moderno e minimalista para as barras de rolagem (sem botões nas extremidades)
        style.layout(
            "Modern.Vertical.TScrollbar",
            [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "children": [
                            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                        ],
                        "sticky": "ns"
                    }
                )
            ]
        )
        style.configure(
            "Modern.Vertical.TScrollbar",
            background="#44475a",
            troughcolor="#181825",
            bordercolor="#181825",
            darkcolor="#44475a",
            lightcolor="#44475a",
            relief="flat",
            borderwidth=0,
            width=10
        )
        style.map(
            "Modern.Vertical.TScrollbar",
            background=[("pressed", "#8be9fd"), ("active", "#4a90e2")]
        )

    # --------------------------------------------------------------------------
    # ABA 1: CONSULTA INDIVIDUAL POR FUNÇÃO ANSI
    # --------------------------------------------------------------------------
    def _construir_aba_consulta(self):
        paned = tk.PanedWindow(self.tab_consulta, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6, bd=0)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_esq = ttk.Frame(paned, width=360)
        paned.add(frame_esq, minsize=300)

        lbl_menu = ttk.Label(frame_esq, text="Tabela ANSI", style="Header.TLabel")
        lbl_menu.pack(anchor="w", padx=5, pady=(5, 2))

        frame_busca = ttk.Frame(frame_esq)
        frame_busca.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(frame_busca, text="Filtrar:").pack(side=tk.LEFT, padx=(0, 5))
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", self._filtrar_lista)
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca, font=("Segoe UI", 10))
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True)

        frame_lista = ttk.Frame(frame_esq)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar_lista = ttk.Scrollbar(
            frame_lista,
            orient=tk.VERTICAL,
            style="Modern.Vertical.TScrollbar"
        )
        self.listbox_ansi = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar_lista.set,
            exportselection=False,
            bg="#282a36",
            fg="#f8f8f2",
            selectbackground="#4a90e2",
            selectforeground="#ffffff",
            font=("Consolas", 10, "bold"),
            activestyle="none",
            bd=0,
            highlightthickness=1,
            highlightcolor="#4a90e2"
        )
        scrollbar_lista.config(command=self.listbox_ansi.yview)
        scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 0))
        self.listbox_ansi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_ansi.bind("<<ListboxSelect>>", self._ao_selecionar_funcao)

        frame_dir = ttk.Frame(paned)
        paned.add(frame_dir, minsize=620)

        self.lbl_titulo_funcao = ttk.Label(frame_dir, text="Selecione uma função ANSI no menu ao lado", style="Header.TLabel")
        self.lbl_titulo_funcao.pack(anchor="w", padx=10, pady=(5, 5))

        frame_texto = ttk.Frame(frame_dir)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scroll_texto = ttk.Scrollbar(
            frame_texto,
            orient=tk.VERTICAL,
            style="Modern.Vertical.TScrollbar"
        )
        self.txt_detalhes = tk.Text(
            frame_texto,
            yscrollcommand=scroll_texto.set,
            bg="#282a36",
            fg="#f8f8f2",
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            padx=15,
            pady=15,
            bd=0,
            state=tk.DISABLED
        )
        scroll_texto.config(command=self.txt_detalhes.yview)
        scroll_texto.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 0))
        self.txt_detalhes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags de formatação visual
        self.txt_detalhes.tag_configure("desc", foreground="#f1fa8c", font=("Segoe UI", 10, "italic"), spacing3=10)
        self.txt_detalhes.tag_configure("subfuncao_header", background="#343746", foreground="#ffffff", font=("Segoe UI", 11, "bold"), spacing1=14, spacing3=6)
        self.txt_detalhes.tag_configure("secao_ea", foreground="#8be9fd", font=("Segoe UI", 10, "bold"), spacing1=6, spacing3=2)
        self.txt_detalhes.tag_configure("secao_bi", foreground="#50fa7b", font=("Segoe UI", 10, "bold"), spacing1=6, spacing3=2)
        self.txt_detalhes.tag_configure("secao_bo", foreground="#ffb86c", font=("Segoe UI", 10, "bold"), spacing1=6, spacing3=2)
        self.txt_detalhes.tag_configure("item", foreground="#f8f8f2", font=("Segoe UI", 10), lmargin1=18, lmargin2=30, spacing1=2)
        self.txt_detalhes.tag_configure("item_opcional", foreground="#f1fa8c", font=("Segoe UI", 10), lmargin1=18, lmargin2=30, spacing1=2)
        self.txt_detalhes.tag_configure("item_logico", foreground="#bd93f9", font=("Segoe UI", 10), lmargin1=18, lmargin2=30, spacing1=2)
        self.txt_detalhes.tag_configure("item_vazio", foreground="#949cbb", font=("Segoe UI", 10, "italic"), lmargin1=18, lmargin2=30, spacing1=2)

        self._popular_listbox()
        if self.listbox_ansi.size() > 0:
            self.listbox_ansi.selection_set(0)
            self._ao_selecionar_funcao(None)

    def _popular_listbox(self, filtro=""):
        self.listbox_ansi.delete(0, tk.END)
        self.chaves_filtradas = []
        filtro = filtro.lower().strip()

        for codigo, dados in ANSI_DATABASE.items():
            texto_exibicao = f"{codigo:>2} - {dados['nome']}"
            sub_nomes = " ".join(dados["subfuncoes"].keys()).lower()
            if (
                filtro in codigo.lower()
                or filtro in dados["nome"].lower()
                or filtro in dados["descricao"].lower()
                or filtro in sub_nomes
            ):
                self.listbox_ansi.insert(tk.END, texto_exibicao)
                self.chaves_filtradas.append(codigo)

    def _filtrar_lista(self, *args):
        self._popular_listbox(self.var_busca.get())

    def _inserir_item_formatado(self, texto):
        if texto.startswith("[Opcional]"):
            self.txt_detalhes.insert(tk.END, f"• {texto}\n", "item_opcional")
        elif texto.startswith("[Lógico]"):
            self.txt_detalhes.insert(tk.END, f"• {texto}\n", "item_logico")
        else:
            self.txt_detalhes.insert(tk.END, f"• {texto}\n", "item")

    def _ao_selecionar_funcao(self, event):
        selecao = self.listbox_ansi.curselection()
        if not selecao:
            return
        idx = selecao[0]
        codigo = self.chaves_filtradas[idx]
        dados = ANSI_DATABASE[codigo]

        self.lbl_titulo_funcao.config(text=f"ANSI {codigo} — {dados['nome']}")

        self.txt_detalhes.config(state=tk.NORMAL)
        self.txt_detalhes.delete("1.0", tk.END)

        self.txt_detalhes.insert(tk.END, f"► Definição Funcional:\n{dados['descricao']}\n", "desc")

        for nome_sub, sub_dados in dados["subfuncoes"].items():
            self.txt_detalhes.insert(tk.END, f"  ■ {nome_sub}  \n", "subfuncao_header")

            # Entradas Analógicas (EAs)
            self.txt_detalhes.insert(tk.END, "  ⚡ Entradas Analógicas (EAs - TC / TP):\n", "secao_ea")
            if sub_dados["ea"]:
                for item in sub_dados["ea"]:
                    self._inserir_item_formatado(item)
            else:
                self.txt_detalhes.insert(tk.END, "• Nenhuma entrada analógica de TC/TP necessária para este item.\n", "item_vazio")

            # Entradas Digitais (BIs)
            self.txt_detalhes.insert(tk.END, "  [BI] Entradas Digitais (Binary Inputs):\n", "secao_bi")
            for item in sub_dados["bi"]:
                self._inserir_item_formatado(item)

            # Saídas Digitais (BOs)
            self.txt_detalhes.insert(tk.END, "  [BO] Saídas Digitais (Binary Outputs):\n", "secao_bo")
            for item in sub_dados["bo"]:
                self._inserir_item_formatado(item)

            self.txt_detalhes.insert(tk.END, "\n")

        self.txt_detalhes.config(state=tk.DISABLED)

    # --------------------------------------------------------------------------
    # ABA 2: CONSOLIDADOR DE WORKSTATEMENT (SEPARADO EM FÍSICOS, OPCIONAIS E LÓGICOS)
    # --------------------------------------------------------------------------
    def _construir_aba_workstatement(self):
        paned = tk.PanedWindow(self.tab_workstatement, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6, bd=0)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_check = ttk.Frame(paned, width=430)
        paned.add(frame_check, minsize=380)

        ttk.Label(
            frame_check,
            text="Selecione os Itens do Workstatement:",
            style="Header.TLabel"
        ).pack(anchor="w", padx=5, pady=5)

        self.canvas_chk = tk.Canvas(frame_check, bg="#282a36", highlightthickness=0)
        scroll_chk = ttk.Scrollbar(
            frame_check,
            orient=tk.VERTICAL,
            command=self.canvas_chk.yview,
            style="Modern.Vertical.TScrollbar"
        )
        self.frame_interno_chk = tk.Frame(self.canvas_chk, bg="#282a36")

        self.frame_interno_chk.bind(
            "<Configure>",
            lambda e: self.canvas_chk.configure(scrollregion=self.canvas_chk.bbox("all"))
        )
        self.canvas_window_id = self.canvas_chk.create_window((0, 0), window=self.frame_interno_chk, anchor="nw")
        self.canvas_chk.configure(yscrollcommand=scroll_chk.set)

        self.canvas_chk.bind(
            "<Configure>",
            lambda e: self.canvas_chk.itemconfigure(self.canvas_window_id, width=e.width)
        )

        self.canvas_chk.bind("<Enter>", lambda e: self.canvas_chk.bind_all("<MouseWheel>", self._rolar_canvas_mousewheel))
        self.canvas_chk.bind("<Leave>", lambda e: self.canvas_chk.unbind_all("<MouseWheel>"))

        self.canvas_chk.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scroll_chk.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 5), pady=5)

        for codigo, dados in ANSI_DATABASE.items():
            lbl_cat = tk.Label(
                self.frame_interno_chk,
                text=f"ANSI {codigo} — {dados['nome']}",
                bg="#343746",
                fg="#8be9fd",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                padx=6,
                pady=2
            )
            lbl_cat.pack(fill=tk.X, padx=4, pady=(8, 2))

            for nome_sub in dados["subfuncoes"].keys():
                chave_unica = (codigo, nome_sub)
                var = tk.BooleanVar(value=False)
                self.checkbox_vars[chave_unica] = var
                chk = tk.Checkbutton(
                    self.frame_interno_chk,
                    text=nome_sub,
                    variable=var,
                    command=self._atualizar_consolidado,
                    bg="#282a36",
                    fg="#f8f8f2",
                    selectcolor="#1e1e2e",
                    activebackground="#282a36",
                    activeforeground="#50fa7b",
                    font=("Segoe UI", 9),
                    anchor="w"
                )
                chk.pack(fill=tk.X, padx=14, pady=1)

        frame_res = ttk.Frame(paned)
        paned.add(frame_res, minsize=560)

        frame_topo_res = ttk.Frame(frame_res)
        frame_topo_res.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_topo_res, text="Lista Consolidada (Físicos / Opcionais / Lógicos)", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(frame_topo_res, text="Exportar CSV / Excel", style="Accent.TButton", command=self._exportar_csv).pack(side=tk.RIGHT, padx=4)
        ttk.Button(frame_topo_res, text="Limpar Seleção", style="Accent.TButton", command=self._limpar_selecao).pack(side=tk.RIGHT, padx=4)

        frame_txt_cons = ttk.Frame(frame_res)
        frame_txt_cons.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scroll_cons = ttk.Scrollbar(
            frame_txt_cons,
            orient=tk.VERTICAL,
            style="Modern.Vertical.TScrollbar"
        )
        self.txt_consolidado = tk.Text(
            frame_txt_cons,
            yscrollcommand=scroll_cons.set,
            bg="#282a36",
            fg="#f8f8f2",
            font=("Consolas", 10),
            wrap=tk.WORD,
            padx=15,
            pady=15,
            bd=0,
            state=tk.DISABLED
        )
        scroll_cons.config(command=self.txt_consolidado.yview)
        scroll_cons.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 0))
        self.txt_consolidado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._atualizar_consolidado()

    def _rolar_canvas_mousewheel(self, event):
        self.canvas_chk.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @staticmethod
    def _extrair_chave_base_e_tag(texto_sinal):
        tag = "Físico"
        texto_limpo = texto_sinal.strip()

        if texto_limpo.startswith("[Opcional]"):
            tag = "Opcional"
            texto_limpo = texto_limpo.replace("[Opcional]", "", 1).strip()
        elif texto_limpo.startswith("[Lógico]"):
            tag = "Lógico"
            texto_limpo = texto_limpo.replace("[Lógico]", "", 1).strip()

        if "Iniciação 79" in texto_limpo and "[Somente em Zona 1" in texto_limpo:
            chave_base = texto_limpo
        else:
            chave_base = texto_limpo.split(" [")[0].strip()

        return tag, chave_base

    @staticmethod
    def _rotulo_curto_subfuncao(nome_sub):
        if "[" in nome_sub and "]" in nome_sub:
            inicio = nome_sub.find("[") + 1
            fim = nome_sub.find("]")
            return nome_sub[inicio:fim]
        return nome_sub.split(" (")[0].strip()

    @staticmethod
    def _registrar_no_grupo(dicionario, chave_base, tipo_io, tag, cod, rotulo):
        if chave_base not in dicionario:
            dicionario[chave_base] = {
                "tipo_io": tipo_io,
                "tag": tag,
                "codigos_ansi": [],
                "subfuncoes": []
            }
        if cod not in dicionario[chave_base]["codigos_ansi"]:
            dicionario[chave_base]["codigos_ansi"].append(cod)
        if rotulo not in dicionario[chave_base]["subfuncoes"]:
            dicionario[chave_base]["subfuncoes"].append(rotulo)

    def _agrupar_sinais_selecionados(self, selecionadas):
        eas_fis, bis_fis, bos_fis = {}, {}, {}
        itens_opcionais = {}
        itens_logicos = {}

        for cod, nome_sub in selecionadas:
            rotulo = self._rotulo_curto_subfuncao(nome_sub)
            sub_dados = ANSI_DATABASE[cod]["subfuncoes"][nome_sub]

            for item in sub_dados["ea"]:
                tag, chave_base = self._extrair_chave_base_e_tag(item)
                self._registrar_no_grupo(eas_fis, chave_base, "EA (Analógica)", tag, cod, rotulo)

            for item in sub_dados["bi"]:
                tag, chave_base = self._extrair_chave_base_e_tag(item)
                if tag == "Opcional":
                    self._registrar_no_grupo(itens_opcionais, chave_base, "BI (Entrada Digital)", "Opcional", cod, rotulo)
                elif tag == "Lógico":
                    self._registrar_no_grupo(itens_logicos, chave_base, "BI (Entrada Digital)", "Lógico", cod, rotulo)
                else:
                    self._registrar_no_grupo(bis_fis, chave_base, "BI (Entrada Digital)", "Físico", cod, rotulo)

            for item in sub_dados["bo"]:
                tag, chave_base = self._extrair_chave_base_e_tag(item)
                if tag == "Opcional":
                    self._registrar_no_grupo(itens_opcionais, chave_base, "BO (Saída Digital)", "Opcional", cod, rotulo)
                elif tag == "Lógico":
                    self._registrar_no_grupo(itens_logicos, chave_base, "BO (Saída Digital)", "Lógico", cod, rotulo)
                else:
                    self._registrar_no_grupo(bos_fis, chave_base, "BO (Saída Digital)", "Físico", cod, rotulo)

        return eas_fis, bis_fis, bos_fis, itens_opcionais, itens_logicos

    def _atualizar_consolidado(self):
        selecionadas = [chave for chave, var in self.checkbox_vars.items() if var.get()]

        self.txt_consolidado.config(state=tk.NORMAL)
        self.txt_consolidado.delete("1.0", tk.END)

        if not selecionadas:
            self.txt_consolidado.insert(
                tk.END,
                "Marque à esquerda os itens exigidos no Workstatement (ex: 21P, 50P, 51P, 79T)\n"
                "para gerar a lista consolidada separada entre Sinais Físicos Principais, Itens [Opcional] e Itens [Lógico]."
            )
            self.txt_consolidado.config(state=tk.DISABLED)
            return

        eas_fis, bis_fis, bos_fis, opcionais, logicos = self._agrupar_sinais_selecionados(selecionadas)
        nomes_sel = [self._rotulo_curto_subfuncao(nome_sub) for _, nome_sub in selecionadas]

        cabecalho = (
            f"========================================================================\n"
            f" ITENS SELECIONADOS ({len(selecionadas)}): {', '.join(nomes_sel)}\n"
            f"========================================================================\n\n"
        )
        self.txt_consolidado.insert(tk.END, cabecalho)

        # BLOCO 1: SINAIS FÍSICOS PRINCIPAIS
        self.txt_consolidado.insert(tk.END, f"--- [1] ENTRADAS ANALÓGICAS (EAs - Total: {len(eas_fis)}) ---\n")
        if eas_fis:
            for idx, (sinal, info) in enumerate(eas_fis.items(), 1):
                self.txt_consolidado.insert(tk.END, f"  EA{idx:02d} [{', '.join(info['subfuncoes'])}]: {sinal}\n")
        else:
            self.txt_consolidado.insert(tk.END, "  Nenhuma Entrada Analógica necessária para os itens selecionados.\n")

        self.txt_consolidado.insert(tk.END, f"\n--- [2] ENTRADAS DIGITAIS FÍSICAS (BIs - Total: {len(bis_fis)}) ---\n")
        if bis_fis:
            for idx, (sinal, info) in enumerate(bis_fis.items(), 1):
                self.txt_consolidado.insert(tk.END, f"  BI{idx:02d} [{', '.join(info['subfuncoes'])}]: {sinal}\n")
        else:
            self.txt_consolidado.insert(tk.END, "  Nenhuma Entrada Digital obrigatória.\n")

        self.txt_consolidado.insert(tk.END, f"\n--- [3] SAÍDAS DIGITAIS FÍSICAS (BOs - Total: {len(bos_fis)}) ---\n")
        if bos_fis:
            for idx, (sinal, info) in enumerate(bos_fis.items(), 1):
                self.txt_consolidado.insert(tk.END, f"  BO{idx:02d} [{', '.join(info['subfuncoes'])}]: {sinal}\n")
        else:
            self.txt_consolidado.insert(tk.END, "  Nenhuma Saída Digital física obrigatória.\n")

        # BLOCO 2: ITENS OPCIONAIS
        self.txt_consolidado.insert(tk.END, f"\n========================================================================\n")
        self.txt_consolidado.insert(tk.END, f"--- [4] ITENS COM TAG [Opcional] (Total: {len(opcionais)}) ---\n")
        if opcionais:
            for idx, (sinal, info) in enumerate(opcionais.items(), 1):
                prefixo = "BI_OPC" if "BI" in info["tipo_io"] else "BO_OPC"
                self.txt_consolidado.insert(
                    tk.END,
                    f"  {prefixo}{idx:02d} [TAG: Opcional | {', '.join(info['subfuncoes'])}]: {sinal}\n"
                )
        else:
            self.txt_consolidado.insert(tk.END, "  Nenhum item opcional associado.\n")

        # BLOCO 3: ITENS LÓGICOS
        self.txt_consolidado.insert(tk.END, f"\n========================================================================\n")
        self.txt_consolidado.insert(tk.END, f"--- [5] ITENS COM TAG [Lógico] (Total: {len(logicos)}) ---\n")
        if logicos:
            for idx, (sinal, info) in enumerate(logicos.items(), 1):
                self.txt_consolidado.insert(
                    tk.END,
                    f"  LOG{idx:02d} [TAG: Lógico | {', '.join(info['subfuncoes'])}]: {sinal}\n"
                )
        else:
            self.txt_consolidado.insert(tk.END, "  Nenhum item lógico associado.\n")

        self.txt_consolidado.config(state=tk.DISABLED)

    def _limpar_selecao(self):
        for var in self.checkbox_vars.values():
            var.set(False)
        self._atualizar_consolidado()

    def _exportar_csv(self):
        selecionadas = [chave for chave, var in self.checkbox_vars.items() if var.get()]
        if not selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos um item ANSI antes de exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV (Excel)", "*.csv"), ("Todos os arquivos", "*.*")],
            initialfile="Mapa_IO_SPCS_Build_3_0.csv"
        )
        if not caminho:
            return

        eas_fis, bis_fis, bos_fis, opcionais, logicos = self._agrupar_sinais_selecionados(selecionadas)

        try:
            with open(caminho, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")

                # TABELA 1: ENTRADAS E SAÍDAS FÍSICAS PRINCIPAIS
                writer.writerow(["=== 1. SINAIS FÍSICOS PRINCIPAIS (EAs, BIs e BOs) ===", "", "", "", "", ""])
                writer.writerow(["CODIGO_IO", "TIPO_IO", "TAG", "FUNCOES_ANSI", "ITENS_ASSOCIADOS", "DESCRICAO_SINAL"])

                for idx, (sinal, info) in enumerate(eas_fis.items(), 1):
                    writer.writerow([
                        f"EA{idx:02d}",
                        info["tipo_io"],
                        "Físico",
                        ", ".join(info["codigos_ansi"]),
                        ", ".join(info["subfuncoes"]),
                        sinal
                    ])

                for idx, (sinal, info) in enumerate(bis_fis.items(), 1):
                    writer.writerow([
                        f"BI{idx:02d}",
                        info["tipo_io"],
                        "Físico",
                        ", ".join(info["codigos_ansi"]),
                        ", ".join(info["subfuncoes"]),
                        sinal
                    ])

                for idx, (sinal, info) in enumerate(bos_fis.items(), 1):
                    writer.writerow([
                        f"BO{idx:02d}",
                        info["tipo_io"],
                        "Físico",
                        ", ".join(info["codigos_ansi"]),
                        ", ".join(info["subfuncoes"]),
                        sinal
                    ])

                # TABELA 2: ITENS OPCIONAIS
                writer.writerow([])
                writer.writerow(["=== 2. ITENS OPCIONAIS (TAG: Opcional) ===", "", "", "", "", ""])
                writer.writerow(["CODIGO_IO", "TIPO_IO", "TAG", "FUNCOES_ANSI", "ITENS_ASSOCIADOS", "DESCRICAO_SINAL"])

                for idx, (sinal, info) in enumerate(opcionais.items(), 1):
                    prefixo = "BI_OPC" if "BI" in info["tipo_io"] else "BO_OPC"
                    writer.writerow([
                        f"{prefixo}{idx:02d}",
                        info["tipo_io"],
                        "Opcional",
                        ", ".join(info["codigos_ansi"]),
                        ", ".join(info["subfuncoes"]),
                        sinal
                    ])

                # TABELA 3: ITENS LÓGICOS
                writer.writerow([])
                writer.writerow(["=== 3. ITENS LÓGICOS (TAG: Lógico) ===", "", "", "", "", ""])
                writer.writerow(["CODIGO_IO", "TIPO_IO", "TAG", "FUNCOES_ANSI", "ITENS_ASSOCIADOS", "DESCRICAO_SINAL"])

                for idx, (sinal, info) in enumerate(logicos.items(), 1):
                    writer.writerow([
                        f"LOG{idx:02d}",
                        info["tipo_io"],
                        "Lógico",
                        ", ".join(info["codigos_ansi"]),
                        ", ".join(info["subfuncoes"]),
                        sinal
                    ])

            messagebox.showinfo("Sucesso", f"Planilha exportada com seções separadas (Físicos, Opcionais e Lógicos) em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", str(e))