# Verificação da seção 3.4.2 — Medições

Reprodução das Tabelas 1 e 2 do trabalho nesta máquina, para conferir se os resultados se mantêm.

## Ambiente

- **processador**: Intel64 Family 6 Model 151 Stepping 2, GenuineIntel
- **nucleos_logicos**: 24
- **sistema**: Windows 11 (10.0.26300)
- **python**: 3.12.10
- **implementacao**: CPython
- **parâmetros**: 20 gerações, 5% de espalhadores, limiar 2, semente 42

## Tabela 2 — divisão do tempo de uma geração (1000×1000)

Mediana de 5 repetições, após aquecimento. Medido em 129 s.

| Etapa | Por geração (s) | Participação (%) | Publicado (s) | Desvio |
|---|---:|---:|---:|---:|
| Varredura das células | 0.712 | 81.6 | 0.638 | +11.5% |
| Cópia da grade (deepcopy) | 0.158 | 18.2 | 0.179 | -11.5% |
| Contagem dos estados (contar_estados) | 0.043 | 4.9 | 0.038 | +12.0% |
| Total | 0.872 | 100.0 | 0.855 | +2.0% |

A varredura é obtida por diferença (`proxima_geracao` − cópia medida à parte), e a contagem é medida isolada — a mesma metodologia descrita no texto.

## Veredito

- **Tabela 2**: total de 0.872 s por geração contra 0,855 s publicados (+2.0%).
  Participações medidas: varredura 82%, cópia 18% e contagem 5% (publicado: 74,6% / 21,0% / 4,4%).
  A Tabela 2 do trabalho foi medida em **outra máquina** (i7-13650HX, Python 3.12.10); os valores absolutos não são diretamente comparáveis, mas a **proporção** entre as etapas deve se manter.
