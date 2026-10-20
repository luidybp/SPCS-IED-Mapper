import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# ==============================================================================
# BANCO DE DADOS DE FUNÇÕES ANSI (PADRÃO IEEE C37.2 / TABELA ANSI SEL & SIEMENS)
# Build 2.0 - 20/10/2026
# ==============================================================================
# Sinais padronizados para permitir agrupamento automático (deduplicação)
# e separação automática em 3 blocos no Consolidador e no Excel (.csv):
#   1. Sinais Físicos Principais (EAs, BIs e BOs obrigatórias)
#   2. Sinais Opcionais (TAG [Opcional])
#   3. Sinais Lógicos (TAG [Lógico])
# ==============================================================================

# --- Entradas Analógicas Padrão (EAs) ---
EA_TC_FASES = "TC do Vão - Fases (IA, IB, IC)"
EA_TC_NEUTRO = "TC de Neutro Físico / Bucha de Neutro ou Toroidal (Canal IN / IY)"
EA_TP_FASES = "TP de Barra ou Linha - Fases (VA, VB, VC)"

# --- Entradas Digitais Padrão (BIs) ---
BI_52AB = "Posição do Disjuntor Tripolar (52a e 52b)"
BI_TP_FUSIVEL = "Estado do Disjuntor Secundário do TP / Fusível Atuado"
BI_MOLA_SF6 = "Disjuntor Pronto: Mola Carregada e Pressão de SF6 Normal"

# --- Saídas Digitais Físicas Padrão (BOs - Linhas/Alimentadores vs. Transformador) ---
BO_TRIP_LINHA = "Disparo (Trip) nas Bobinas de Abertura 1 e 2 do Disjuntor"
BO_TRIP_TR_AT = "Disparo (Trip) nas Bobinas de Abertura 1 e 2 do Disjuntor AT"
BO_TRIP_TR_BT = "Disparo (Trip) nas Bobinas de Abertura 1 e 2 do Disjuntor BT"
BO_ACIONA_86 = "Acionamento do Relé de Bloqueio (86)"
BO_BLOQUEIO_79 = "Bloqueio Definitivo do Religamento Automático (79 Lockout)"

# --- Sinais com TAG [Opcional] (Separados no Excel conforme Item 4 do To-Do) ---
BO_PARTIDA_79_OPC = "[Opcional] Partida de Religamento Automático (Iniciação 79)"
BO_PARTIDA_79_Z1_OPC = "[Opcional] Partida de Religamento Automático (Iniciação 79) [Somente em Zona 1 ou via Teleproteção]"

# --- Sinais com TAG [Lógico] (Separados no Excel conforme Item 5 do To-Do) ---
BO_PARTIDA_50BF_LOG = "[Lógico] Partida de Falha de Disjuntor (Iniciação 50BF)"
BO_ALARME_SCADA_LOG = "[Lógico] Sinalização / Alarme de Atuação para SCADA e Anunciador (30)"


ANSI_DATABASE = {
    "21": {
        "nome": "Relé de distância",
        "descricao": "Mede a impedância da linha (Z = V/I) em zonas de proteção (Z1, Z2, Z3, ZReversa) para determinar a distância da falta em linhas de transmissão.",
        "subfuncoes": {
            "21P (Distância de Fase)": {
                "ea": [
                    EA_TC_FASES + " [Sem necessidade de TC de neutro para loops Fase-Fase]",
                    EA_TP_FASES
                ],
                "bi": [
                    BI_52AB,
                    BI_TP_FUSIVEL + " [Bloqueia 21P por perda de potencial]",
                    "Recepção de Sinal de Teleproteção (85 RX)",
                    "[Opcional] Bloqueio Externo por Oscilação de Potência (68 PSB)",
                    "[Opcional] Chave de Bloqueio da Função 21 (43-21)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_79_Z1_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ],
                # "sel": "TODO: SEL-421/411L/311L -> M1P, M2P, M3P, Z1T, Z2T, LOP",
                # "siemens": "TODO: SIPROTEC 4 (7SA522/7SA6) / SIPROTEC 5 (7SA87)"
            },
            "21N / 21G (Distância de Terra)": {
                "ea": [
                    EA_TC_FASES + " + Corrente de Sequência Zero (3I0 / IN) para compensação de terra (k0)",
                    EA_TP_FASES,
                    "TC do Circuito Paralelo (3I0m) [Opcional: apenas para compensação mútua em linhas duplas]"
                ],
                "bi": [
                    BI_52AB,
                    BI_TP_FUSIVEL + " [Bloqueia 21N/21G por perda de potencial]",
                    "Recepção de Sinal de Teleproteção (85 RX)",
                    "[Opcional] Bloqueio Externo por Oscilação de Potência (68 PSB)",
                    "[Opcional] Chave de Bloqueio da Função 21 (43-21)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_79_Z1_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "SOTF (Fechamento sob Falta - Switch Onto Fault)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES
                ],
                "bi": [
                    BI_52AB + " [Detecta linha fora de serviço antes do fechamento]",
                    "Comando de Fechamento Manual do Disjuntor (Ativa janela temporal de SOTF)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "24": {
        "nome": "Relé de volts por hertz",
        "descricao": "Opera quando a relação entre a tensão e a frequência (V/Hz) excede um valor predefinido, protegendo transformadores de potência e geradores contra sobreexcitação (saturação magnética do núcleo).",
        "subfuncoes": {
            "24 (Sobreexcitação Volts/Hertz - V/Hz)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_52AB,
                    BI_TP_FUSIVEL + " [Bloqueia função 24 em caso de falha no TP]",
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 24"
                ],
                "bo": [
                    "Alarme de Sobreexcitação V/Hz - 1º Estágio",
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86 + " [2º Estágio de Trip por Sobreexcitação]",
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "25": {
        "nome": "Dispositivo de sincronização ou verificação de sincronismo",
        "descricao": "Verifica magnitude de tensão (V), frequência (f) e ângulo de fase (θ) entre dois pontos antes de permitir o fechamento do disjuntor, além das lógicas de Barra Morta / Linha Viva.",
        "subfuncoes": {
            "25 (Verificação de Sincronismo e Barra/Linha Viva/Morta)": {
                "ea": [
                    "TP Lado 1 / Barra (VA, VB, VC ou VAB)",
                    "TP Lado 2 / Linha - Canal de Sincronismo (VSync / VX) [Atenção: verificar conflito físico do 4º canal de tensão caso haja 59N em Delta Aberto no mesmo IED]"
                ],
                "bi": [
                    "Requisição de Fechamento Manual do Disjuntor (Local / Remoto / SCADA)",
                    "Requisição de Fechamento pelo Religador Automático (79)",
                    "Estado do Disjuntor Secundário do TP de Barra / Fusível Atuado [Bloqueia permissão por Barra Morta]",
                    "Estado do Disjuntor Secundário do TP de Linha / Fusível Atuado [Bloqueia permissão por Linha Morta]",
                    "[Opcional] Chave de Bypass de Sincronismo (43-25)"
                ],
                "bo": [
                    "Permissão de Fechamento do Disjuntor (Liberado na malha da Bobina de Fechamento 52-BC / 52-BFE)",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "26": {
        "nome": "Dispositivo térmico do equipamento",
        "descricao": "Termômetro mecânico ou monitor eletrônico que mede diretamente a temperatura do óleo isolante do transformador/reator (frequentemente acoplado à imagem térmica 49).",
        "subfuncoes": {
            "26 (Temperatura do Óleo por Contato Seco)": {
                "ea": [],
                "bi": [
                    "Alarme de Temperatura Elevada do Óleo - 1º Estágio (26OA)",
                    "Desligamento (Trip) por Temperatura Muito Elevada do Óleo - 2º Estágio (26OT)",
                    "[Opcional] Alarme de Falha do Monitor de Temperatura (Autodiagnóstico)"
                ],
                "bo": [
                    # Nota de revisão (Item 11): Confirmar padrão de BOs com o Patrick
                    "Comando de Ligação de Ventilação Forçada do Transformador",
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86 + " [2º Estágio de Trip]",
                    BO_PARTIDA_50BF_LOG + " [Supervisionada por contato 52a]",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "27": {
        "nome": "Relé de subtensão",
        "descricao": "Opera quando a tensão monitorada cai abaixo de um valor predeterminado (aplicado em barramentos CA via TP ou supervisão de alimentação auxiliar CC via relé dedicado).",
        "subfuncoes": {
            "27 (Subtensão de Fase CA)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Obrigatório para bloquear o 27 e impedir trip falso ao desarmar o disjuntor secundário do TP]",
                    BI_52AB + " [Opcional: inibe atuação com o vão propositalmente desenergizado]",
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 27"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Permissão de Transferência Automática de Barramentos / Serviços Auxiliares",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "27CC (Supervisão de Subtensão de Alimentação CC)": {
                "ea": [],
                "bi": [
                    "Contato seco do Relé Auxiliar Supervisor de Tensão CC (27CC) de 125 Vcc / 48 Vcc"
                ],
                "bo": [
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "30": {
        "nome": "Relé anunciador",
        "descricao": "Dispositivo de reinicialização manual ou remota que fornece indicações visuais e sonoras (painel de alarme ou LEDs retentivos) de atuação de proteções e anormalidades.",
        "subfuncoes": {
            "30 (Anunciador de Alarmes / Sinalização de Painel)": {
                "ea": [],
                "bi": [
                    "Contatos secos de alarmes e trips de campo (Ex: 63 Buchholz, 26/49 Temperatura, 71 Nível de Óleo, Baixa Pressão SF6)",
                    "Contatos de supervisão interna do painel (Ex: 72 Disjuntor CC Desarmado, 27CC, 74TC Falha Bobina, 86 Atuado, Watchdog IED)",
                    "Botoeiras de Reconhecimento (ACK), Silenciar Buzina, Teste de Lâmpadas e Reset"
                ],
                "bo": [
                    "Acionamento de Buzina / Alarme Sonoro do Painel"
                ]
            }
        }
    },
    "32": {
        "nome": "Relé direcional de potência",
        "descricao": "Opera quando o fluxo de potência ativa (W) ou reativa (VAr) ultrapassa um limiar em uma direção específica (ex: proteção contra motorização/potência reversa em geradores ou controle de fluxo em interligações). [Nota: Confirmar padrão de BOs com o Patrick]",
        "subfuncoes": {
            "32P / 32Q (Direcional de Potência Ativa / Reativa)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES
                ],
                "bi": [
                    BI_52AB,
                    BI_TP_FUSIVEL + " [Bloqueia elemento 32 por perda de potencial]",
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 32"
                ],
                "bo": [
                    # Nota de revisão (Itens 11 e 13): Confirmar com o Patrick as BOs desta função
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    # ==========================================================================
    # MARCADOR DE REVISÃO (ITEM 13): Revisado manualmente pelo Luidy até a 32.
    # As funções abaixo (43 a 94) já receberam as padronizações globais do To-Do.
    # ==========================================================================
    "43": {
        "nome": "Dispositivo de transferência ou seleção manual",
        "descricao": "Chave seletora operada manualmente no painel ou virtualmente no IED para transferir modos de comando (Local/Remoto) ou habilitar/desabilitar funções (79, 85, 51N, ERAC).",
        "subfuncoes": {
            "43 (Chave Seletora de Comando / Função)": {
                "ea": [],
                "bi": [
                    "Contato Posição 1 da Chave (Ex: Comando LOCAL / Função HABILITADA)",
                    "Contato Posição 2 da Chave (Ex: Comando REMOTO / Função DESABILITADA)"
                ],
                "bo": [
                    "Permissão ou Bloqueio na malha de comando/proteção",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "46": {
        "nome": "Relé de corrente de reversão de fase ou de equilíbrio de fase",
        "descricao": "Opera quando as correntes polifásicas estão em sequência inversa, desequilibradas (corrente de sequência negativa I2) ou com perda de fase (cabo partido / abertura monopolar).",
        "subfuncoes": {
            "46 (Desequilíbrio de Corrente / Sequência Negativa I2 / Cabo Partido)": {
                "ea": [
                    EA_TC_FASES + " [O IED calcula I2 e a relação I2/I1 a partir das três fases]"
                ],
                "bi": [
                    BI_52AB,
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 46"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "47": {
        "nome": "Relé de tensão de sequência de fase ou de equilíbrio de fase",
        "descricao": "Opera quando as tensões polifásicas estão na sequência de fase incorreta (inversão de fases A-B-C) ou apresentam desequilíbrio severo (tensão de sequência negativa V2).",
        "subfuncoes": {
            "47 (Sequência de Fase e Desequilíbrio de Tensão V2)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Bloqueia elemento 47 para evitar atuação indevida]",
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 47"
                ],
                "bo": [
                    "Bloqueio de Fechamento do Disjuntor (52) por Inversão de Sequência de Fase",
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "49": {
        "nome": "Relé térmico de máquina ou transformador",
        "descricao": "Opera quando a temperatura de um equipamento excede o limite seguro, estimada por modelo térmico de corrente (I²t) no IED ou lida via sensores RTD (PT100) / contatos de imagem térmica.",
        "subfuncoes": {
            "49 (Sobrecarga Térmica por Corrente - Modelo I²t no IED)": {
                "ea": [
                    EA_TC_FASES
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo / Reset da Memória Térmica da Função 49"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "49RTD / 49 Externo (Imagem Térmica dos Enrolamentos do TR)": {
                "ea": [
                    "Sinais de RTD (PT100) ou Transdutores de 4-20 mA [Quando lidos via módulo analógico/fibra pelo IED]"
                ],
                "bi": [
                    "Contato de Alarme de Temperatura do Enrolamento - 1º Estágio (49A)",
                    "Contato de Trip de Temperatura do Enrolamento - 2º Estágio (49T)",
                    "Contato de Partida de Ventilação Forçada",
                    "[Opcional] Alarme de Falha do Monitor de Temperatura (Autodiagnóstico)"
                ],
                "bo": [
                    "Comando de Ligação de Ventilação Forçada do Transformador",
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86 + " [2º Estágio de Trip]",
                    BO_PARTIDA_50BF_LOG + " [Supervisionada por contato 52a]",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "50": {
        "nome": "Relé de sobrecorrente instantâneo",
        "descricao": "Opera sem atraso intencional (ou com tempo definido curto) para faltas severas. ATENÇÃO À NOMENCLATURA DE TERRA: Na SEL, 'N' é Neutro Medido (IN) e 'G' é Residual Calculado (3I0). Na SIEMENS/IEC é o inverso: '50N' é Residual Calculado (3I0) e '50G/50Ns' é o Neutro Medido.",
        "subfuncoes": {
            "50P / 50L (Sobrecorrente Instantânea de Fase)": {
                "ea": [
                    EA_TC_FASES + " [Não utiliza TC de Neutro]"
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo por Seletividade Lógica (Recepção ZSI dos relés a jusante)",
                    "[Opcional] Bloqueio Externo por Chave ou Grupo de Ajuste Alternativo"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Bloqueio de Seletividade Lógica (ZSI para relé a montante)",
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Neutro Medido [SEL: 50N | SIEMENS: 50G / 50Ns] (Canal IN Físico)": {
                "ea": [
                    EA_TC_NEUTRO + " [Medição física direta no 4º canal de corrente; não requer TCs de fase para este elemento]"
                ],
                "bi": [
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-50N/51N)",
                    "[Opcional] Bloqueio Externo por Seletividade Lógica de Terra (ZSI)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Residual Calculado 3I0 [SEL: 50G | SIEMENS: 50N] (Soma IA+IB+IC)": {
                "ea": [
                    EA_TC_FASES + " [O IED calcula 3I0 = IA + IB + IC internamente ou no retorno comum; não requer TC separado na bucha de neutro]"
                ],
                "bi": [
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-50N/51N)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "50Q (Sobrecorrente Instantânea de Sequência Negativa - 3I2)": {
                "ea": [
                    EA_TC_FASES + " [Calculado internamente pelo IED para faltas assimétricas]"
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 50Q"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "50BF (Proteção contra Falha de Disjuntor - Breaker Failure)": {
                "ea": [
                    EA_TC_FASES + " [Detecção de corrente subsistente após comando de Trip]"
                ],
                "bi": [
                    "Iniciação Externa de Falha de Disjuntor (BFI - Recebe sinal de Trip de outros relés de proteção do vão)",
                    BI_52AB + " [Supervisão para falhas mecânicas em trips sem corrente elevada, como 63, 49 e 59]"
                ],
                "bo": [
                    "Re-Trip 50BF (1º Estágio instantâneo ou < 50 ms: novo comando nas Bobinas 1 e 2 do próprio disjuntor)",
                    "Disparo 50BF (2º Estágio ~100 a 250 ms: aciona Relé de Bloqueio 86BF para abrir disjuntores adjacentes da barra)",
                    BO_BLOQUEIO_79,
                    "Envio de Transferência Direta de Disparo (85 DTT TX) para abrir o terminal remoto",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "50STUB (Sobrecorrente de Barra Stub - Arranjo Disjuntor e Meio)": {
                "ea": [
                    "TC do Disjuntor da Barra (IA, IB, IC) + TC do Disjuntor Central (IA, IB, IC) que delimitam o Stub"
                ],
                "bi": [
                    "Chave Seccionadora de Saída de Linha Aberta (89L-b = Fechado) [Habilita 50STUB apenas quando a linha está isolada]"
                ],
                "bo": [
                    "Disparo (Trip) Imediato nos dois Disjuntores que formam o Stub (Disjuntor de Barra e Disjuntor Central)",
                    BO_BLOQUEIO_79,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "51": {
        "nome": "Relé de sobrecorrente temporizado CA",
        "descricao": "Opera com atraso inversamente proporcional à magnitude da corrente (curvas IEC/IEEE). ATENÇÃO À NOMENCLATURA DE TERRA: Na SEL, '51N' é Neutro Medido (IN) e '51G' é Residual Calculado (3I0). Na SIEMENS/IEC, '51N' é Residual Calculado (3I0) e '51G/51Ns' é o Neutro Medido.",
        "subfuncoes": {
            "51P / 51L (Sobrecorrente Temporizada de Fase)": {
                "ea": [
                    EA_TC_FASES + " [Não utiliza TC de Neutro]"
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 51P"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Sinal de Partida (Pickup 51P) para Seletividade Lógica ou Oscilografia",
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Neutro Medido [SEL: 51N | SIEMENS: 51G / 51Ns] (Canal IN Físico)": {
                "ea": [
                    EA_TC_NEUTRO
                ],
                "bi": [
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-50N/51N)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Residual Calculado 3I0 [SEL: 51G | SIEMENS: 51N] (Soma IA+IB+IC)": {
                "ea": [
                    EA_TC_FASES + " [Calcula 3I0 = IA + IB + IC internamente; não exige TC de neutro separado]"
                ],
                "bi": [
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-50N/51N)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "51Q (Sobrecorrente Temporizada de Sequência Negativa - 3I2)": {
                "ea": [
                    EA_TC_FASES
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 51Q"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "51V (Sobrecorrente Temporizada com Restrição/Controle de Tensão)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES + " [Reduz o pickup ou libera o elemento 51 quando a tensão cai durante faltas]"
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Bloqueia o modo de restrição de tensão se houver atuação de fusível do TP]"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "52": {
        "nome": "Disjuntor de corrente alternada",
        "descricao": "Dispositivo de manobra e interrupção de correntes de carga e curto-circuito. Abaixo estão os sinais necessários no IED para comando, supervisão de estado e intertravamento do disjuntor.",
        "subfuncoes": {
            "52 (Comando e Supervisão de Disjuntor CA)": {
                "ea": [
                    EA_TC_FASES + " [Monitoramento de desgaste de contatos I²t e confirmação de corrente zero]"
                ],
                "bi": [
                    BI_52AB,
                    BI_MOLA_SF6,
                    "Baixa Pressão de Gás SF6 - 1º Estágio (Alarme)",
                    "Baixa Pressão de Gás SF6 - 2º Estágio (Bloqueio de Operação de Abertura e Fechamento)",
                    "Chave Local/Remoto do Pátio em Posição Remoto (Permissão de comando pelo SPCS)",
                    "Relé de Bloqueio Desarmado (86 Normal - Permissão de Fechamento)",
                    "Discordância de Polos Atuada (Em disjuntores de comando monopolar)"
                ],
                "bo": [
                    "Comando de Fechamento do Disjuntor (Bobina de Fechamento 52-BC / 52-BFE)",
                    "Comando de Abertura Operacional do Disjuntor (52-BA)",
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "59": {
        "nome": "Relé de sobretensão",
        "descricao": "Opera quando a tensão excede um valor predeterminado. Abaixo estão separadas as variantes de Sobretensão de Fase (59P), Deslocamento de Neutro por TP em Delta Aberto (59N), Residual Calculada (59G) e Sequência Negativa (59Q).",
        "subfuncoes": {
            "59P (Sobretensão de Fase / Fase-Fase)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_52AB,
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 59P"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Transferência Direta de Disparo (85 DTT TX) [Comum em LTs longas por Efeito Ferranti]",
                    BO_BLOQUEIO_79,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "59N (Sobretensão de Neutro Medida via TP em Delta Aberto)": {
                "ea": [
                    "TP em Ligação Delta Aberto (Canal VN / VS = 3V0 medido fisicamente) [Atenção: ocupa o 4º canal de tensão do IED; verificar compatibilidade caso o mesmo IED possua função 25]"
                ],
                "bi": [
                    "Estado do Disjuntor Secundário do TP em Delta Aberto / Fusível Atuado",
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 59N"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "59G (Sobretensão Residual Calculada - 3V0)": {
                "ea": [
                    EA_TP_FASES + " [O IED calcula 3V0 = VA + VB + VC internamente; não requer enrolamento de TP em Delta Aberto nem ocupa o 4º canal VS]"
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Obrigatório bloquear 59G na perda de uma fase do TP, pois fusível atuado gera falso 3V0 elevado]"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "59Q (Sobretensão de Sequência Negativa - V2)": {
                "ea": [
                    EA_TP_FASES + " [Calculado internamente pelo IED]"
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Obrigatório bloquear 59Q em caso de fusível atuado]"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "60": {
        "nome": "Relé de balanço de tensão ou corrente",
        "descricao": "Opera quando há diferença de tensão ou corrente entre dois circuitos (utilizado para Supervisão de Perda de Potencial do TP / Fusível Atuado e para desequilíbrio de bancos de capacitores).",
        "subfuncoes": {
            "60 (Supervisão de Perda de Potencial do TP / Fusível Atuado)": {
                "ea": [
                    EA_TP_FASES,
                    EA_TC_FASES + " [Compara presença de V2/3V0 sem presença correspondente de I2/3I0 para detectar fusível atuado]"
                ],
                "bi": [
                    BI_TP_FUSIVEL
                ],
                "bo": [
                    "[Lógico] Bloqueio Imediato das Funções Dependentes de Tensão (21, 24, 25, 27, 32, 47, 51V, 59G, 59Q, 67, 68, 78) [Nota: o 81 é supervisionado por subtensão 27B81]",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "60C (Desequilíbrio de Neutro de Banco de Capacitores - Dupla Estrela)": {
                "ea": [
                    "TC de Interligação entre os Neutros do Banco de Capacitores (IN / Iunb)"
                ],
                "bi": [
                    BI_52AB
                ],
                "bo": [
                    "Alarme de Desequilíbrio de Capacitores - 1º Estágio (Queima de unidades fusíveis/latas)",
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "62": {
        "nome": "Relé de parada ou abertura temporizada",
        "descricao": "Relé temporizador auxiliar utilizado em conjunto com outras funções para introduzir atrasos lógicos de abertura, fechamento, escalonamento seletivo ou falha de disjuntor (62BF).",
        "subfuncoes": {
            "62 (Temporizador Lógico Auxiliar)": {
                "ea": [],
                "bi": [
                    "Sinal de Partida da Temporização (Ex: Atuação de relé externo ou condição lógica de intertravamento)"
                ],
                "bo": [
                    "Sinal Temporizado de Disparo, Abertura ou Alarme após esgotamento do tempo (Pickup / Dropout Timer)"
                ]
            }
        }
    },
    "63": {
        "nome": "Relé de pressão",
        "descricao": "Opera com valores dados de pressão ou taxa de variação de pressão de gás/óleo (Relé Buchholz 63B, Pressão Súbita 63PS/63SP, Válvula de Alívio de Pressão 63VS/63PR e Fluxo do Comutador Sob Carga 63OLTC).",
        "subfuncoes": {
            "63B (Relé Buchholz de Transformador / Reator)": {
                "ea": [],
                "bi": [
                    "Relé Buchholz - 1º Estágio: Acúmulo de Gás / Alarme (63BA)",
                    "Relé Buchholz - 2º Estágio: Fluxo de Óleo / Disparo (63BT)"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86 + " [2º Estágio de Trip]",
                    BO_PARTIDA_50BF_LOG + " [Supervisionada por contato 52a]",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "63PS / 63VS (Pressão Súbita 63SP / Válvula de Alívio de Pressão 63PR / 63OLTC)": {
                "ea": [],
                "bi": [
                    "Relé de Pressão Súbita / Válvula de Alívio de Pressão do Tanque Principal - Trip (63PS / 63VS)",
                    "Relé de Fluxo de Óleo / Pressão do Comutador Sob Carga - Trip (63OLTC)"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86,
                    BO_PARTIDA_50BF_LOG + " [Supervisionada por contato 52a]",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "64": {
        "nome": "Relé detector de terra",
        "descricao": "Opera na falha de isolamento para a terra de máquinas, transformadores ou barramentos (inclui Proteção de Cuba/Tanque/Massa 64T e Falta à Terra de Estator/Barramento).",
        "subfuncoes": {
            "64T / 51C (Proteção de Tanque / Cuba / Carcaça de Transformador)": {
                "ea": [
                    "TC de Aterramento da Cuba/Tanque do Transformador (1 TC dedicado no cabo de aterramento do tanque à malha)"
                ],
                "bi": [
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 64"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "67": {
        "nome": "Relé direcional de sobrecorrente CA",
        "descricao": "Opera para um valor desejado de sobrecorrente fluindo em uma direção predeterminada (Frente / Reverso). ATENÇÃO: Na SEL, '67N' usa canal IN medido e '67G' usa residual calculado (3I0). Na SIEMENS/IEC, '67N' é o residual calculado (3I0) e '67G/67Ns' é o neutro medido.",
        "subfuncoes": {
            "67P (Sobrecorrente Direcional de Fase)": {
                "ea": [
                    EA_TC_FASES + " [Não requer TC de Neutro]",
                    EA_TP_FASES + " [Necessário para polarização em quadratura 90°]"
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Bloqueia o 67P ou converte para 50P/51P não-direcional conforme filosofia]",
                    "Recepção de Sinal de Teleproteção (85 RX)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Neutro Medido [SEL: 67N | SIEMENS: 67G / 67Ns] (Operação por Canal IN)": {
                "ea": [
                    EA_TC_NEUTRO + " [Corrente de operação]",
                    "Grandeza de Polarização: TP para Tensão Residual (3V0) E/OU TC de Bucha de Neutro do Transformador (IPOL)"
                ],
                "bi": [
                    BI_TP_FUSIVEL,
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-67N)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "Residual Calculado 3I0 [SEL: 67G | SIEMENS: 67N] (Operação por IA+IB+IC)": {
                "ea": [
                    EA_TC_FASES + " [O IED calcula 3I0 de operação e I2]",
                    EA_TP_FASES + " [O IED calcula 3V0 e V2 para polarização sem exigir TC de neutro ou TP em delta aberto]"
                ],
                "bi": [
                    BI_TP_FUSIVEL,
                    "[Opcional] Chave de Bloqueio de Proteção de Neutro/Terra (43-67N)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "67Q (Sobrecorrente Direcional de Sequência Negativa)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES + " [Polarizado por tensão de sequência negativa V2]"
                ],
                "bi": [
                    BI_TP_FUSIVEL
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    "Envio de Sinal de Teleproteção (85 TX)",
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "68": {
        "nome": "Relé de bloqueio por oscilação de potência",
        "descricao": "Diferente do relé 86 (que trava o disjuntor aberto), a função 68 (Power Swing Blocking - PSB) monitora a taxa de variação da impedância aparente (dZ/dt) através de blinders/polígonos concêntricos no plano R-X para distinguir uma oscilação eletromecânica síncrona de um curto-circuito, gerando um sinal lógico que BLOQUEIA temporariamente as zonas de distância (21) para evitar desligamentos indevidos de linhas sãs.",
        "subfuncoes": {
            "68 (Bloqueio de Distância por Oscilação de Potência - PSB)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES + " [Cálculo da trajetória de impedância Z(t) e taxa de variação dZ/dt no plano R-X]"
                ],
                "bi": [
                    BI_TP_FUSIVEL
                ],
                "bo": [
                    "[Lógico] Bloqueio Interno das Zonas de Distância (21P / 21G) selecionadas durante oscilação de potência estável",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "71": {
        "nome": "Dispositivo detector de nível",
        "descricao": "Opera com valores dados de nível ou taxa de variação de nível de líquidos/gases (ex: Indicador Magnético de Nível de Óleo do tanque principal e do comutador do transformador).",
        "subfuncoes": {
            "71 (Nível de Óleo de Transformador / Reator)": {
                "ea": [],
                "bi": [
                    "Nível de Óleo Mínimo / Máximo do Tanque Principal - Alarme (71A)",
                    "Nível de Óleo Crítico do Comutador / Tanque - Desligamento/Trip (71T, quando aplicável na filosofia)"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86 + " [Caso o estágio de Trip por Nível Crítico esteja habilitado]",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "72": {
        "nome": "Disjuntor de corrente contínua",
        "descricao": "Disjuntor usado para fechar e interromper um circuito de potência ou comando de corrente contínua (125 Vcc / 48 Vcc) nos painéis de SPCS.",
        "subfuncoes": {
            "72 (Supervisão de Minidisjuntores CC do Painel)": {
                "ea": [],
                "bi": [
                    "Série de contatos auxiliares (NA/NF) dos disjuntores CC (72.1, 72.2, 72.3...) monitorando alimentação de IEDs, bobinas e sinalização"
                ],
                "bo": [
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "74": {
        "nome": "Relé de alarme",
        "descricao": "Relé diferente do anunciador (30) usado para operar em conexão com um alarme visual/sonoro ou para supervisionar continuamente a integridade da malha das Bobinas de Disparo do Disjuntor (74TC / Trip Circuit Supervision).",
        "subfuncoes": {
            "74TC / TCS (Supervisão do Circuito de Disparo - Bobinas 1 e 2)": {
                "ea": [],
                "bi": [
                    "BI 1 de Supervisão da Bobina de Abertura (Em série com 52a - monitora continuidade com o disjuntor FECHADO)",
                    "BI 2 de Supervisão da Bobina de Abertura (Em série com 52b - monitora continuidade com o disjuntor ABERTO)"
                ],
                "bo": [
                    "Bloqueio de Fechamento do Disjuntor caso o circuito de abertura esteja rompido",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "78": {
        "nome": "Relé de medição de ângulo de defasagem",
        "descricao": "Opera com um ângulo de defasagem predeterminado entre duas tensões/correntes ou protege contra perda de sincronismo / escorregamento de polos (Out-of-Step Tripping - OST).",
        "subfuncoes": {
            "78 (Perda de Sincronismo / Out-of-Step Tripping - OST)": {
                "ea": [
                    EA_TC_FASES,
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL,
                    "[Opcional] Bloqueio Externo por Chave ou Condição Lógica da Função 78"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "79": {
        "nome": "Relé de religamento CA",
        "descricao": "Controla o fechamento e travamento automático de um disjuntor de corrente alternada após desligamento por falta transitória em linhas aéreas (Tripolar ou Monopolar/Tripolar).",
        "subfuncoes": {
            "79T (Religamento Automático Tripolar)": {
                "ea": [],
                "bi": [
                    BI_52AB,
                    BI_MOLA_SF6,
                    "Chave Seletora de Religamento (43-79: Religamento em Serviço / Fora de Serviço)",
                    "Partida Externa de Religamento (79RI - Quando a proteção principal está em outro IED)",
                    "[Opcional] Bloqueio Externo do Religamento (79DTL / Drive-to-Lockout: Atuação de 86, 50BF, Abertura Manual, Z2/Z3, ERAC 81U)"
                ],
                "bo": [
                    "Comando de Fechamento Automático do Disjuntor (Bobina de Fechamento 52-BC / 52-BFE, supervisionado pelo 25)",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "79M (Religamento Automático Monopolar / Tripolar - Linhas de AT/EAT)": {
                "ea": [],
                "bi": [
                    "Posição Individual dos Polos do Disjuntor: Fase A (52a_A/52b_A), Fase B (52a_B/52b_B) e Fase C (52a_C/52b_C)",
                    BI_MOLA_SF6,
                    "Chave Seletora de Modo do Religamento (43-79: Monopolar / Tripolar / Monopolar+Tripolar / Desligado)",
                    "Partida Seletiva por Fase (Trip Monopolar Fase A, B ou C vindo do 21 / 87L)",
                    "Discordância de Polos Atuada (62PD) / Falta Evolutiva ou Polifásica (Força Trip Tripolar e Lockout)"
                ],
                "bo": [
                    "Comando de Fechamento Individual por Polo: Bobina de Fechamento Polo A (52-BC_A), Polo B (52-BC_B) e Polo C (52-BC_C)",
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "81": {
        "nome": "Relé de frequência",
        "descricao": "Opera com um valor predeterminado de frequência (f) ou taxa de variação de frequência (df/dt). Abaixo estão separadas as variantes de Subfrequência (81U - ERAC), Sobrefrequência (81O) e Taxa de Variação df/dt (81R - ROCOF).",
        "subfuncoes": {
            "81U (Subfrequência - Esquema Regional de Alívio de Carga / ERAC)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL + " [Nota: internamente o 81 também é supervisionado por subtensão 27B81]",
                    "Chave de Habilitação / Desabilitação do ERAC (43-ERAC)",
                    BI_52AB
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "81O (Sobrefrequência)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL,
                    BI_52AB
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "81R (Taxa de Variação de Frequência - df/dt / ROCOF)": {
                "ea": [
                    EA_TP_FASES
                ],
                "bi": [
                    BI_TP_FUSIVEL,
                    "Chave de Habilitação do Estágio df/dt (43-ERAC)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "85": {
        "nome": "Receptor de sinal de onda portadora ou fio-piloto",
        "descricao": "Equipamento de comunicação de teleproteção (via fibra óptica dedicada, OPGW, multiplexador ou onda portadora). Abaixo estão separados os esquemas Permissivos (POTT/PUTT), Bloqueio (DCB) e Transferência Direta de Disparo (DTT).",
        "subfuncoes": {
            "85 POTT / PUTT (Comparação Direcional Permissiva por Sobrealcance / Subalcance)": {
                "ea": [],
                "bi": [
                    "Recepção de Permissão de Teleproteção (85 RX - acelera o disparo de 21 Zona 2 ou 67N Direto)",
                    "Alarme de Falha / Perda do Canal de Teleproteção (85 Channel Fail)",
                    "Chave de Teleproteção em Serviço / Fora de Serviço (43-85)"
                ],
                "bo": [
                    "Transmissão de Permissão de Teleproteção (85 TX - acionado por partida de Zona 1 no PUTT ou Zona 2 / 67N Direto no POTT)",
                    "Eco / Weak Infeed Trip (Retransmissão de permissão quando o terminal local tem disjuntor aberto ou fonte fraca)",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "85 DCB (Comparação Direcional por Bloqueio)": {
                "ea": [],
                "bi": [
                    "Recepção de Sinal de Bloqueio (85 RX - BLOQUEIA o disparo da Zona 2 sobrealcançada e do 67N Direto para faltas externas)",
                    "Alarme de Falha / Perda do Canal de Teleproteção (85 Channel Fail)",
                    "Chave de Teleproteção em Serviço / Fora de Serviço (43-85)"
                ],
                "bo": [
                    "Transmissão de Sinal de Bloqueio (85 TX - acionado pela Zona Reversa 21-Z3R ou 67N Reverso ao detectar falta atrás do terminal local)",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "85 DTT (Transferência Direta de Disparo - Direct Transfer Trip)": {
                "ea": [],
                "bi": [
                    "Recepção de Transferência Direta de Disparo - Canal 1 e Canal 2 (85 DTT RX1 / RX2)",
                    "Alarme de Falha / Perda do Canal de Teleproteção (85 Channel Fail)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_BLOQUEIO_79,
                    "Envio de Transferência Direta de Disparo (85 DTT TX - acionado por 50BF, 59, 87R/Reator)",
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "86": {
        "nome": "Relé de bloqueio e desligamento",
        "descricao": "Relé auxiliar biestável (Lockout) operado eletricamente com reposição (reset) manual, que dispara o disjuntor e trava mecanicamente/eletricamente seu circuito de fechamento após faltas graves (87, 63, 49, 50BF).",
        "subfuncoes": {
            "86 (Relé de Bloqueio Físico / Lockout)": {
                "ea": [],
                "bi": [
                    "Contato Auxiliar do Relé 86 (86a / 86b) conectado à BI do IED para indicar 'Relé 86 Atuado' e bloquear 79/fechamento",
                    "[Opcional] Supervisão da Bobina do Relé 86"
                ],
                "bo": [
                    BO_ACIONA_86,
                    "Ação direta dos contatos do 86 físico: Abre Bobinas 1 e 2 do Disjuntor, corta malha da Bobina de Fechamento (52-BC) e inicia 50BF",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "87": {
        "nome": "Relé de proteção diferencial",
        "descricao": "Opera com base na diferença fasorial entre as correntes que entram e saem da zona protegida. Abaixo estão separadas as variantes Diferencial de Transformador (87T), Terra Restrita (87N/REF), Barras (87B) e Linha (87L).",
        "subfuncoes": {
            "87T (Diferencial Percentual de Transformador)": {
                "ea": [
                    "TC do Lado de Alta Tensão (Winding 1: IA1, IB1, IC1)",
                    "TC do Lado de Baixa Tensão (Winding 2: IA2, IB2, IC2)",
                    "TC do Enrolamento Terciário (Winding 3: IA3, IB3, IC3 - Quando houver 3 enrolamentos)"
                ],
                "bi": [
                    BI_52AB + " [Disjuntores de AT e BT]",
                    "[Opcional] Chave de Bloqueio da Proteção Diferencial (43-87T)"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86,
                    "Bloqueio do Comutador Sob Carga (OLTC)",
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "87N / REF (Diferencial de Terra Restrita de Transformador)": {
                "ea": [
                    EA_TC_FASES + " [Enrolamento em Estrela Aterrada para cálculo de 3I0]",
                    EA_TC_NEUTRO + " [Mede a corrente que retorna pelo aterramento da bucha de neutro do transformador]"
                ],
                "bi": [
                    "[Opcional] Chave de Bloqueio da Proteção 87N/REF"
                ],
                "bo": [
                    BO_TRIP_TR_AT,
                    BO_TRIP_TR_BT,
                    BO_ACIONA_86,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            },
            "87B (Diferencial de Barras)": {
                "ea": [
                    "TCs de todos os vãos conectados ao barramento (Linhas, Transformadores, Alimentadores e Disjuntor de Interligação/Transferência)"
                ],
                "bi": [
                    "Posição de todas as Chaves Seccionadoras Seletoras de Barra (89-1a/b, 89-2a/b) para a lógica dinâmica de Réplica/Imagem de Barras",
                    BI_52AB + " [Disjuntores dos vãos e interligação]",
                    "Iniciação Externa de Falha de Disjuntor (BFI de cada vão, caso o 50BF seja processado no 87B)",
                    "[Opcional] Chave de Bloqueio da Diferencial de Barras (43-87B)"
                ],
                "bo": [
                    BO_ACIONA_86 + " [Relé 86B de todos os disjuntores conectados à barra em falta]",
                    BO_BLOQUEIO_79,
                    "Envio de Transferência Direta de Disparo (85 DTT TX) para terminais remotos",
                    BO_ALARME_SCADA_LOG
                ]
            },
            "87L (Diferencial Longitudinal de Linha)": {
                "ea": [
                    EA_TC_FASES + " [As correntes do terminal remoto são recebidas via fibra óptica dedicada / canal C37.94]",
                    EA_TP_FASES + " [Opcional para o 87L puro, mas obrigatório caso o mesmo IED execute 21 de retaguarda]"
                ],
                "bi": [
                    BI_52AB,
                    "Alarme de Falha de Canal Óptico 87L",
                    "[Opcional] Chave de Bloqueio da Função 87L (43-87L)"
                ],
                "bo": [
                    BO_TRIP_LINHA,
                    BO_PARTIDA_79_OPC,
                    BO_PARTIDA_50BF_LOG,
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "89": {
        "nome": "Chave seccionadora de linha",
        "descricao": "Chave utilizada como meio de desconexão/isolamento físico visível em circuitos de alta tensão. Sem capacidade de abertura sob carga, exige intertravamento completo no SPCS.",
        "subfuncoes": {
            "89 / 57 (Comando e Intertravamento de Seccionadora e Chave de Aterramento)": {
                "ea": [],
                "bi": [
                    "Contato Auxiliar Normalmente Aberto da Seccionadora (89a - Indica Fechada)",
                    "Contato Auxiliar Normalmente Fechado da Seccionadora (89b - Indica Aberta)",
                    "Contatos Auxiliares da Lâmina/Chave de Aterramento Associada (57a/57b ou 89AT-a/89AT-b)",
                    BI_52AB + " [52b confirma disjuntor aberto para manobra sem carga]",
                    "Posição das demais Seccionadoras do Vão/Barra (Intertravamento de pátio / transferência de barra)",
                    "Chave Local/Remoto no Painel do Motor no Pátio",
                    "Disjuntor Termomagnético do Motor da Seccionadora Normal"
                ],
                "bo": [
                    "Permissão de Intertravamento (Energiza relé de liberação da malha de força/comando do motor da seccionadora)",
                    "Comando de Abertura da Seccionadora (89-BA)",
                    "Comando de Fechamento da Seccionadora (89-BC / 89-BFE)",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "90": {
        "nome": "Dispositivo de regulação",
        "descricao": "Opera para regular uma grandeza (como tensão ou potência reativa) dentro de determinados limites, atuando no Comutador de Derivação Sob Carga (OLTC / CDC) de transformadores.",
        "subfuncoes": {
            "90 (Regulador Automático de Tensão / Controle de Tap OLTC)": {
                "ea": [
                    "TP do Barramento Regulado - Secundário do Transformador (VA, VB, VC ou VAB)",
                    "TC do Secundário do Transformador (IA, IB, IC para compensação de queda na linha LDC e paralelismo)"
                ],
                "bi": [
                    "Sinalização de Posição de Tap (Código BCD, Matriz de Contatos ou 4-20 mA)",
                    "Comutador em Operação / Em Trânsito",
                    "Tap em Limite Máximo / Limite Mínimo",
                    "Chave Manual / Automático (43-90) e Mestre / Seguidor / Individual",
                    "[Opcional] Bloqueio Externo por Sobrecorrente (50/51) ou Subtensão Severa (27)"
                ],
                "bo": [
                    "Comando de Elevar Tap (Raise)",
                    "Comando de Abaixar Tap (Lower)",
                    BO_ALARME_SCADA_LOG
                ]
            }
        }
    },
    "94": {
        "nome": "Relé de desligamento ou de desligamento livre",
        "descricao": "Opera para desligar um disjuntor ou equipamento (sem trava mecânica retentiva, diferentemente do 86), permitindo que o circuito volte a ser fechado após a extinção do comando de abertura.",
        "subfuncoes": {
            "94 (Relé Auxiliar Multiplicador de Disparo / Trip)": {
                "ea": [],
                "bi": [
                    "Contato auxiliar de supervisão ou confirmação de atuação do relé 94 (quando monitorado pelo IED)"
                ],
                "bo": [
                    BO_TRIP_LINHA
                ]
            }
        }
    }
}


# ==============================================================================
# CLASSE PRINCIPAL DA INTERFACE GRÁFICA (GUI WINDOWS)
# ==============================================================================
class SPCSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Item 1 & Item 7: Removida a inscrição tripla de autoria; título limpo com Build 2.0
        self.title("SPCS IED Mapper — Mapeamento de EAs, BIs e BOs (Build 2.0)")
        self.geometry("1240x760")
        self.minsize(1000, 640)
        self.configure(bg="#1e1e2e")

        self._configurar_estilo()
        self.checkbox_vars = {}

        # Barra de Cabeçalho Superior (Sem repetição de autoria)
        frame_header_top = ttk.Frame(self)
        frame_header_top.pack(fill=tk.X, padx=14, pady=(10, 0))
        ttk.Label(
            frame_header_top,
            text="⚡ SPCS IED Mapper — Engenharia de Proteção, Controle e Supervisão",
            style="Header.TLabel"
        ).pack(side=tk.LEFT)
        ttk.Label(
            frame_header_top,
            text="Build 2.0 — 20/10/2026",
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

        # Barra de Rodapé Fixa (Único local com a assinatura + Build 2.0 e Data)
        frame_footer = tk.Frame(self, bg="#181825", height=28)
        frame_footer.pack(fill=tk.X, side=tk.BOTTOM)
        lbl_footer_esq = tk.Label(
            frame_footer,
            text="  Padrão ANSI / IEEE C37.2 | Build 2.0 (20/10/2026)",
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

    # --------------------------------------------------------------------------
    # ABA 1: CONSULTA INDIVIDUAL POR FUNÇÃO ANSI
    # --------------------------------------------------------------------------
    def _construir_aba_consulta(self):
        paned = tk.PanedWindow(self.tab_consulta, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6, bd=0)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_esq = ttk.Frame(paned, width=360)
        paned.add(frame_esq, minsize=300)

        lbl_menu = ttk.Label(frame_esq, text="Tabela ANSI (Padrão SEL / IEEE C37.2)", style="Header.TLabel")
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

        scrollbar_lista = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
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
        scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_ansi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_ansi.bind("<<ListboxSelect>>", self._ao_selecionar_funcao)

        frame_dir = ttk.Frame(paned)
        paned.add(frame_dir, minsize=620)

        self.lbl_titulo_funcao = ttk.Label(frame_dir, text="Selecione uma função ANSI no menu ao lado", style="Header.TLabel")
        self.lbl_titulo_funcao.pack(anchor="w", padx=10, pady=(5, 5))

        frame_texto = ttk.Frame(frame_dir)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scroll_texto = ttk.Scrollbar(frame_texto, orient=tk.VERTICAL)
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
        scroll_texto.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_detalhes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags de formatação visual (incluindo destaque para [Opcional] e [Lógico])
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
                # Item 10 do To-Do: Alterado para "para este item"
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
        scroll_chk = ttk.Scrollbar(frame_check, orient=tk.VERTICAL, command=self.canvas_chk.yview)
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
        scroll_chk.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

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

        scroll_cons = ttk.Scrollbar(frame_txt_cons, orient=tk.VERTICAL)
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
        scroll_cons.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_consolidado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._atualizar_consolidado()

    def _rolar_canvas_mousewheel(self, event):
        self.canvas_chk.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @staticmethod
    def _extrair_chave_base_e_tag(texto_sinal):
        """
        Identifica se o sinal possui a TAG [Opcional] ou [Lógico] no início e
        extrai o texto base (sem notas explicativas finais entre colchetes) para agrupamento.
        """
        tag = "Físico"
        texto_limpo = texto_sinal.strip()

        if texto_limpo.startswith("[Opcional]"):
            tag = "Opcional"
            texto_limpo = texto_limpo.replace("[Opcional]", "", 1).strip()
        elif texto_limpo.startswith("[Lógico]"):
            tag = "Lógico"
            texto_limpo = texto_limpo.replace("[Lógico]", "", 1).strip()

        # Mantém a nota de Zona 1 na iniciação do 79 da função 21 conforme Item 4c
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
        """
        Separa os sinais consolidados em:
          1. Físicos Principais (eas_fis, bis_fis, bos_fis)
          2. Itens com TAG 'Opcional' (itens_opcionais)
          3. Itens com TAG 'Lógico' (itens_logicos)
        """
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

        # BLOCO 2: ITENS OPCIONAIS (Separados conforme Item 4 do To-Do)
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

        # BLOCO 3: ITENS LÓGICOS (Separados conforme Item 5 do To-Do)
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
            initialfile="Mapa_IO_SPCS_Build_2_0.csv"
        )
        if not caminho:
            return

        eas_fis, bis_fis, bos_fis, opcionais, logicos = self._agrupar_sinais_selecionados(selecionadas)

        try:
            with open(caminho, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")

                # --------------------------------------------------------------
                # TABELA 1: ENTRADAS E SAÍDAS FÍSICAS PRINCIPAIS
                # --------------------------------------------------------------
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

                # --------------------------------------------------------------
                # TABELA 2: ITENS OPCIONAIS (SEPARADOS NO EXCEL - ITEM 4 DO TO-DO)
                # --------------------------------------------------------------
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

                # --------------------------------------------------------------
                # TABELA 3: ITENS LÓGICOS (SEPARADOS NO EXCEL - ITEM 5 DO TO-DO)
                # --------------------------------------------------------------
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


if __name__ == "__main__":
    app = SPCSApp()
    app.mainloop()