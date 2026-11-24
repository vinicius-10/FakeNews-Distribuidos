# Verificação da seção 3.4.2 — Medições

Reprodução das Tabelas 1 e 2 do trabalho nesta máquina, para conferir se os resultados se mantêm.

> **Correção (23/nov/2026):** a primeira versão deste arquivo calculava o total da Tabela 2 sem a
> contagem dos estados (só `proxima_geracao`), o que fazia as participações somarem 104,6%. O
> script foi corrigido (o total agora é varredura + cópia + contagem, como na tabela publicada) e a
> Tabela 2 abaixo foi recalculada a partir das mesmas medianas, sem nova medição. As conclusões
> sobre "linearidade" e "efeito de cache" foram retiradas: os dados não as sustentam (ver Veredito).

## Ambiente

- **processador**: Intel64 Family 6 Model 151 Stepping 2, GenuineIntel (Intel Core i9-12900F)
- **nucleos_logicos**: 24
- **sistema**: Windows 11 (10.0.26300)
- **python**: 3.12.10
- **implementacao**: CPython
- **parâmetros**: 20 gerações, 5% de espalhadores, limiar 2, semente 42

## Tabela 1 — tempo do laço de gerações (código fornecido)

Mediana de 3 repetições, após aquecimento. Medido em 386 s. O desvio é em relação à Tabela 1 do
relatório, medida na mesma máquina em Python 3.11.7 (4,16 / 16,46 / 65,88 s), a versão de toda a
bateria principal. O relatório cita estes valores em 3.12.10 no texto, logo depois da tabela.

| Grade | Células | Tempo (s) | Por geração (s) | Por célula e geração (µs) | Desvio em relação a 3.11.7 |
|---|---:|---:|---:|---:|---:|
| 500× 500 | 250.000 | 4,27 | 0,214 | 0,85 | +2,8% |
| 1000× 1000 | 1.000.000 | 19,07 | 0,953 | 0,95 | +15,9% |
| 2000× 2000 | 4.000.000 | 73,58 | 3,679 | 0,92 | +11,7% |

Numa segunda rodada completa, a grade de 500² deu 4,41 s e a de 2000², 81,5 s (cerca de 10% de
variação entre rodadas na grade maior).

## Tabela 2 — divisão do tempo de uma geração (1000×1000)

Mediana de 5 repetições, após aquecimento. Medido em 138 s. A varredura é obtida por diferença
(`proxima_geracao` − cópia medida à parte), e a contagem é medida isolada — a mesma metodologia
descrita no texto. O total é a soma das três etapas.

| Etapa | Por geração (s) | Participação (%) | Publicado (s) | Desvio |
|---|---:|---:|---:|---:|
| Varredura das células | 0,759 | 77,9 | 0,638 | +19,0% |
| Cópia da grade (deepcopy) | 0,172 | 17,7 | 0,179 | −3,7% |
| Contagem dos estados (contar_estados) | 0,043 | 4,4 | 0,038 | +13,4% |
| Total | 0,974 | 100,0 | 0,855 | +13,9% |

O valor publicado foi medido em **outra máquina** (i7-13650HX, Python 3.12.10); os valores absolutos
não são diretamente comparáveis, só a proporção entre as etapas.

## Veredito

- **Tabela 1**: em Python 3.12.10 o código do professor ficou de 3% a 16% mais lento que em 3.11.7
  na mesma máquina. O custo por célula e geração ficou entre 0,85 e 0,95 µs, sem tendência com o
  tamanho (sobe de 500² para 1000² e cai de 1000² para 2000²); multiplicar o número de células por
  16 multiplicou o tempo por 17,2. A diferença está dentro da variação entre rodadas (~10% na grade
  maior), então o resultado é compatível com o crescimento linear em L·C.
- **Tabela 2**: participações de 77,9% / 17,7% / 4,4%, contra 74,6% / 21,0% / 4,4% publicados. A
  ordem das etapas e a conclusão (a varredura domina e a cópia é perto de um quinto do tempo) se
  mantêm.
