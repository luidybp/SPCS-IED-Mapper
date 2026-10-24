# ==============================================================================
# MÓDULO 3: PONTO DE ENTRADA DA APLICAÇÃO (main.py)
# Inicializa e executa a interface gráfica do SPCS IED Mapper.
# ==============================================================================

from interface import SPCSApp


def main():
    app = SPCSApp()
    app.mainloop()


if __name__ == "__main__":
    main()