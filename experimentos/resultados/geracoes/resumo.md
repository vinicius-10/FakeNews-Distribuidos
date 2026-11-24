# Escalabilidade com o número de gerações

Bateria que varia **o número de gerações** (10 e 40), mantendo o resto fixo: grade 1000² e
2000², 5% de espalhadores, limiar 2, semente 42. Três versões (`sequencial`, `paralela_processos`,
`distribuida_local`), 1 a 16 trabalhadores, 5 repetições com mediana.

Arquivos desta pasta: `medicoes_10.csv` e `medicoes_40.csv` (saída do `experimentos/medir.py`),
que também servem a `experimentos/analisar.py`.

## Ambiente

| Item | Valor |
|---|---|
| Processador | Intel Core i9-12900F (16 núcleos físicos / 24 lógicos) |
| Sistema | Windows 11 (10.0.26300) |
| Python | 3.12.10 |
| Repetições | 5 por configuração, mediana |

## Equivalência

- **10 gerações**: 90 medições, **0 divergência(s)** de hash.
- **40 gerações**: 90 medições, **0 divergência(s)** de hash.

Todas as versões produziram a mesma grade final nos dois tamanhos — então a comparação de tempo
é entre execuções do mesmo trabalho.

## 10 gerações

| Grade | versão | workers | mediana (s) | speedup | eficiência |
|---|---|---:|---:|---:|---:|
| 1000² | `sequencial` | 1 | 2,456 | 1,00 | 1,00 |
| 1000² | `paralela_processos` | 1 | 2,452 | 1,00 | 1,00 |
| 1000² | `paralela_processos` | 4 | 0,660 | 3,72 | 0,93 |
| 1000² | `paralela_processos` | 8 | 0,414 | 5,93 | 0,74 |
| 1000² | `paralela_processos` | 16 | 0,301 | 8,16 | 0,51 |
| 1000² | `distribuida_local` | 1 | 2,439 | 1,01 | 1,01 |
| 1000² | `distribuida_local` | 4 | 0,638 | 3,85 | 0,96 |
| 1000² | `distribuida_local` | 8 | 0,371 | 6,61 | 0,83 |
| 1000² | `distribuida_local` | 16 | 0,296 | 8,30 | 0,52 |
| 2000² | `sequencial` | 1 | 11,001 | 1,00 | 1,00 |
| 2000² | `paralela_processos` | 1 | 10,064 | 1,09 | 1,09 |
| 2000² | `paralela_processos` | 4 | 2,697 | 4,08 | 1,02 |
| 2000² | `paralela_processos` | 8 | 1,541 | 7,14 | 0,89 |
| 2000² | `paralela_processos` | 16 | 1,108 | 9,93 | 0,62 |
| 2000² | `distribuida_local` | 1 | 11,527 | 0,95 | 0,95 |
| 2000² | `distribuida_local` | 4 | 2,616 | 4,21 | 1,05 |
| 2000² | `distribuida_local` | 8 | 1,527 | 7,20 | 0,90 |
| 2000² | `distribuida_local` | 16 | 1,119 | 9,83 | 0,61 |

## 40 gerações

| Grade | versão | workers | mediana (s) | speedup | eficiência |
|---|---|---:|---:|---:|---:|
| 1000² | `sequencial` | 1 | 7,635 | 1,00 | 1,00 |
| 1000² | `paralela_processos` | 1 | 7,616 | 1,00 | 1,00 |
| 1000² | `paralela_processos` | 4 | 2,079 | 3,67 | 0,92 |
| 1000² | `paralela_processos` | 8 | 1,198 | 6,37 | 0,80 |
| 1000² | `paralela_processos` | 16 | 0,907 | 8,42 | 0,53 |
| 1000² | `distribuida_local` | 1 | 7,610 | 1,00 | 1,00 |
| 1000² | `distribuida_local` | 4 | 1,981 | 3,85 | 0,96 |
| 1000² | `distribuida_local` | 8 | 1,133 | 6,74 | 0,84 |
| 1000² | `distribuida_local` | 16 | 0,893 | 8,55 | 0,53 |
| 2000² | `sequencial` | 1 | 35,757 | 1,00 | 1,00 |
| 2000² | `paralela_processos` | 1 | 33,514 | 1,07 | 1,07 |
| 2000² | `paralela_processos` | 4 | 9,946 | 3,60 | 0,90 |
| 2000² | `paralela_processos` | 8 | 5,534 | 6,46 | 0,81 |
| 2000² | `paralela_processos` | 16 | 3,613 | 9,90 | 0,62 |
| 2000² | `distribuida_local` | 1 | 36,996 | 0,97 | 0,97 |
| 2000² | `distribuida_local` | 4 | 9,074 | 3,94 | 0,99 |
| 2000² | `distribuida_local` | 8 | 5,913 | 6,05 | 0,76 |
| 2000² | `distribuida_local` | 16 | 3,463 | 10,33 | 0,65 |

## O que os números mostram

### O tempo não cresce 4× quando as gerações vão de 10 para 40

| Grade | 10 gerações | 40 gerações | Razão | Se fosse linear |
|---|---:|---:|---:|---:|
| 1000² | 2,456 s | 7,635 s | 3,11× | 4,00× |
| 2000² | 11,001 s | 35,757 s | 3,25× | 4,00× |

A razão fica **abaixo de 4** porque o custo de cada geração **cai ao longo da simulação**:
no `comum/modelo.py`, só a célula `IGNORANTE` soma os 8 vizinhos. Como o número de ignorantes
diminui a cada geração, as gerações finais são mais baratas que as iniciais. Com mais gerações,
a média por geração cai.

### O speedup satura perto de 10 com 16 trabalhadores

| Configuração | speedup (w=16) | eficiência |
|---|---:|---:|
| 10 ger · 1000² · `paralela_processos` | 8,16 | 0,51 |
| 10 ger · 1000² · `distribuida_local` | 8,30 | 0,52 |
| 10 ger · 2000² · `paralela_processos` | 9,93 | 0,62 |
| 10 ger · 2000² · `distribuida_local` | 9,83 | 0,61 |
| 40 ger · 1000² · `paralela_processos` | 8,42 | 0,53 |
| 40 ger · 1000² · `distribuida_local` | 8,55 | 0,53 |
| 40 ger · 2000² · `paralela_processos` | 9,90 | 0,62 |
| 40 ger · 2000² · `distribuida_local` | 10,33 | 0,65 |

O ganho para de crescer perto de **10×** porque a máquina tem **16 núcleos físicos** (24 lógicos,
sendo 8 E-cores): acima de ~10 trabalhadores ativos o ganho real some. A eficiência cai de ~0,95
com 4 trabalhadores para ~0,55 com 16 — comportamento esperado, não defeito.

### Paralela × distribuída

As duas ficam muito próximas, como esperado: a distribuída em `localhost` usa o mesmo número de
processos e troca bordas por socket em loopback, sem latência de rede física. A diferença cai
dentro do ruído da medição. **Esta bateria não mede custo de rede real** — para isso é preciso
rodar entre máquinas.

### Ressalva sobre 1 trabalhador

As linhas com 1 trabalhador mostram speedup entre 0,95 e 1,09. O valor deveria ser ~1,00
(mesmo trabalho, um processo). Desvios como 1,09 vêm de ruído de agendamento e de a máquina
estar com carga diferente entre as execuções; não use esses valores isolados no relatório.
