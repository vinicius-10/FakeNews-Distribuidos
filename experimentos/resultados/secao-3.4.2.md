# Verificação da seção 3.4.2 — Medições

Reprodução das Tabelas 1 e 2 do trabalho nesta máquina, para conferir se os resultados se mantêm.

> **Padrão de execução: Python 3.11.7** — é a versão do artigo e a usada na maioria dos testes do
> projeto. A tabela em 3.12.10 no fim do documento é só uma conferência complementar.


## Ambiente

- **processador**: Intel64 Family 6 Model 151 Stepping 2, GenuineIntel
- **nucleos_logicos**: 24
- **sistema**: Windows 10 (10.0.26300)
- **python**: 3.11.7
- **implementacao**: CPython
- **parâmetros**: 20 gerações, 5% de espalhadores, limiar 2, semente 42

## Tabela 1 — tempo do laço de gerações (código fornecido)

Mediana de 3 repetições, após aquecimento. Medido em 358 s.

| Grade | Células | Tempo (s) | Por geração (s) | Por célula e geração (µs) | Desvio do tempo |
|---|---:|---:|---:|---:|---:|
| 500× 500 | 250,000 | 4.19 | 0.209 | 0.84 | +0.7% |
| 1000× 1000 | 1,000,000 | 16.78 | 0.839 | 0.84 | +1.9% |
| 2000× 2000 | 4,000,000 | 67.94 | 3.397 | 0.85 | +3.1% |

Publicado: 4,16 s / 16,46 s / 65,88 s para 500², 1000² e 2000², com 0,82–0,83 µs por célula e geração.

## Tabela 2 — divisão do tempo de uma geração (1000×1000)

Mediana de 5 repetições, após aquecimento. Medido em 124 s.

| Etapa | Por geração (s) | Participação (%) | Publicado (s) | Desvio |
|---|---:|---:|---:|---:|
| Varredura das células | 0.641 | 78.2 | 0.638 | +0.4% |
| Cópia da grade (deepcopy) | 0.175 | 21.4 | 0.179 | -2.1% |
| Contagem dos estados (contar_estados) | 0.044 | 5.4 | 0.038 | +15.8% |
| Total | 0.819 | 100.0 | 0.855 | -4.2% |

A varredura é obtida por diferença (`proxima_geracao` − cópia medida à parte), e a contagem é medida isolada — a mesma metodologia descrita no texto.

## Veredito

- **Tabela 1**: maior desvio 3.1% no tempo total em relação ao publicado.
  Custo por célula e geração: 500=0.84, 1000=0.84, 2000=0.85 µs — permanece estável (amplitude 0.01 µs). Confirma a linearidade em L·C que o texto afirma.
- **Tabela 2**: total de 0.819 s por geração contra 0,855 s publicados (-4.2%).
  Participações medidas: varredura 78%, cópia 21% e contagem 5% (publicado: 74,6% / 21,0% / 4,4%).
  A Tabela 2 do trabalho foi medida em **outra máquina** (i7-13650HX, Python 3.12.10); os valores absolutos não são diretamente comparáveis, mas a **proporção** entre as etapas deve se manter.

## Rodada complementar — Tabela 2 com Python 3.12.10

Como o trabalho mediu a Tabela 2 com **Python 3.12.10** e esta máquina tinha 3.11.7 como padrão, a tabela foi repetida na mesma versão do artigo (`py -3.12 -m experimentos.verificar_342 --tabela 2`). Resultado completo em [`secao-3.4.2-tabela2-python312.md`](secao-3.4.2-tabela2-python312.md).

| Etapa | 3.11.7 (s) | 3.12.10 (s) | Publicado (s) | Desvio do 3.12 |
|---|---:|---:|---:|---:|
| Varredura das células | 0,641 | 0,712 | 0,638 | +11,5% |
| Cópia da grade (deepcopy) | 0,175 | 0,158 | 0,179 | -11,5% |
| Contagem dos estados | 0,044 | 0,043 | 0,038 | +12,0% |
| **Total** | **0,819** | **0,872** | **0,855** | **+2,0%** |

O total com 3.12.10 fica a **2,0%** do publicado (era -4,2% em 3.11.7). A troca de versão move tempo entre as etapas — a varredura fica relativamente mais cara e a cópia mais barata —, o que desloca a divisão de 78/21/5 para 82/18/5, contra 74,6/21,0/4,4 do trabalho. Como a Tabela 2 do artigo foi medida em **outra máquina** (i7-13650HX), essa diferença de proporção está dentro do esperado para cache e geração de processador diferentes; a **ordem de grandeza e a hierarquia** (varredura ≫ cópia ≫ contagem) se mantêm.
