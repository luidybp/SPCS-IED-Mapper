# SPCS IED Mapper — Mapeamento de EAs, BIs e BOs (Padrão ANSI / IEEE C37.2)

Aplicativo desktop para Windows desenvolvido em Python voltado à Engenharia de Sistemas de Proteção, Controle e Supervisão (SPCS) de subestações de energia elétrica.

## Objetivo do Projeto
Auxiliar projetistas e engenheiros de SPCS na tradução dos requisitos do *Workstatement* em listas de **Entradas Analógicas (EAs)**, **Entradas Digitais (BIs)** e **Saídas Digitais (BOs)** para dimensionamento de IEDs (baseado nas filosofias **SEL** e **SIEMENS SIPROTEC**).

## Funcionalidades Principais
- **Consulta Detalhada por Função ANSI (IEEE C37.2):** Separação granular entre subfunções.
- **Equivalência SEL vs. SIEMENS:** Diferenças de nomenclatura de terra entre fabricantes (`50N/51N/67N` vs. `50G/51G/67G`).
- **Consolidador de Workstatement com Agrupamento Inteligente:** Deduplicação automática de sinais físicos comuns entre múltiplas funções (como `52a/52b`, `60/VTS`, `52-BT1/BT2`), fornecendo a contagem real de portas de hardware necessárias no IED.
- **Exportação para CSV / Excel:** Geração imediata da planilha de mapeamento de I/O consolidada.

## 🚀 Como Executar
- **Via Executável (Sem precisar de Python):** Baixe e execute o arquivo `dist/SPCS_IED_Mapper.exe` (ou na seção *Releases* ao lado).
- **Via Código-Fonte:**
  ```bash
  python spcs_ied_mapper.py