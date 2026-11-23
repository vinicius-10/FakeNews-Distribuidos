# Verificação da seção 3.4.2 — Medições

Reprodução das Tabelas 1 e 2 do trabalho nesta máquina, para conferir se os resultados se mantêm.

## Ambiente

- **processador**: Intel64 Family 6 Model 151 Stepping 2, GenuineIntel
- **nucleos_logicos**: 24
- **sistema**: Windows 11 (10.0.26300)
- **python**: 3.12.10
- **implementacao**: CPython
- **parâmetros**: 20 gerações, 5% de espalhadores, limiar 2, semente 42

## Tabela 1 — tempo do laço de gerações (código fornecido)

Mediana de 3 repetições, após aquecimento. Medido em 386 s.

| Grade | Células | Tempo (s) | Por geração (s) | Por célula e geração (µs) | Desvio do tempo |
|---|---:|---:|---:|---:|---:|
| 500× 500 | 250,000 | 4.27 | 0.214 | 0.85 | +2.8% |
| 1000× 1000 | 1,000,000 | 19.07 | 0.953 | 0.95 | +15.9% |
| 2000× 2000 | 4,000,000 | 73.58 | 3.679 | 0.92 | +11.7% |

Publicado: 4,16 s / 16,46 s / 65,88 s para 500², 1000² e 2000², com 0,82–0,83 µs por célula e geração.

## Tabela 2 — divisão do tempo de uma geração (1000×1000)

Mediana de 5 repetições, após aquecimento. Medido em 138 s.

| Etapa | Por geração (s) | Participação (%) | Publicado (s) | Desvio |
|---|---:|---:|---:|---:|
| Varredura das células | 0.759 | 81.5 | 0.638 | +19.0% |
| Cópia da grade (deepcopy) | 0.172 | 18.5 | 0.179 | -3.7% |
| Contagem dos estados (contar_estados) | 0.043 | 4.6 | 0.038 | +13.4% |
| Total | 0.932 | 100.0 | 0.855 | +9.0% |

A varredura é obtida por diferença (`proxima_geracao` − cópia medida à parte), e a contagem é medida isolada — a mesma metodologia descrita no texto.

## Veredito

- **Tabela 1**: maior desvio 15.9% no tempo total em relação ao publicado.
  Custo por célula e geração: 500=0.85, 1000=0.95, 2000=0.92 µs — variou (12% entre o menor e o maior tamanho). A linearidade em L·C NÃO se confirmou neste ambiente: a grade maior ficou proporcionalmente mais cara (efeito de cache).
- **Tabela 2**: total de 0.932 s por geração contra 0,855 s publicados (+9.0%).
  Participações medidas: varredura 82%, cópia 18% e contagem 5% (publicado: 74,6% / 21,0% / 4,4%).
  A Tabela 2 do trabalho foi medida em **outra máquina** (i7-13650HX, Python 3.12.10); os valores absolutos não são diretamente comparáveis, mas a **proporção** entre as etapas deve se manter.
