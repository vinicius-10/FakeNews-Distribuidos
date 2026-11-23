# Custo da versão sequencial fornecida

Gerado por `python -m experimentos.custo_sequencial`.

## Perfil de uma geração (grade 1000 × 1000, 5% de espalhadores, limiar 2, 20 gerações)

Mediana de 5 repetições. Máquina: 13th Gen Intel(R) Core(TM) i7-13650HX, Windows 11 (10.0.26300), Python 3.12.10.

| Etapa | Tempo total (s) | Por geração (s) | % |
|---|---|---|---|
| deepcopy | 3.5863 | 0.17931 | 21.0 |
| varredura | 12.7590 | 0.63795 | 74.6 |
| contar_estados | 0.7536 | 0.03768 | 4.4 |
| total | 17.0988 | 0.85494 | 100.0 |

O `deepcopy` foi medido à parte, numa cópia da mesma grade; a varredura é `proxima_geracao` menos esse tempo (estimativa).

### Custo por célula conforme o estado

Reta de mínimos quadrados do tempo da varredura (mediana por geração) contra o número de ignorantes na grade de entrada (20 gerações, de 440,412 a 951,228 ignorantes):

| Custo por célula ignorante (µs) | Custo por célula de outro estado (µs) | Razão | Correlação |
|---|---|---|---|
| 1.017 | 0.061 | 16.8 | 0.9993 |

## Limiar × percentual inicial (grade 1000 × 1000, até não haver espalhadores)

| Limiar | % inicial | Espalhadores iniciais | Gerações até parar | Pico de espalhadores | Alcance final |
|---|---|---|---|---|---|
| 1 | 1% | 9,944 | 27 | 166,388 | 100.00% |
| 1 | 2% | 19,792 | 15 | 229,601 | 100.00% |
| 1 | 5% | 48,772 | 10 | 351,922 | 100.00% |
| 1 | 10% | 95,127 | 7 | 498,684 | 100.00% |
| 2 | 1% | 9,944 | 264 | 3,485 | 14.33% |
| 2 | 2% | 19,792 | 163 | 10,537 | 25.17% |
| 2 | 5% | 48,772 | 56 | 55,899 | 57.90% |
| 2 | 10% | 95,127 | 29 | 157,460 | 90.76% |
| 3 | 1% | 9,944 | 2 | 58 | 1.00% |
| 3 | 2% | 19,792 | 3 | 404 | 2.02% |
| 3 | 5% | 48,772 | 3 | 5,069 | 5.40% |
| 3 | 10% | 95,127 | 4 | 29,889 | 12.77% |

## Memória da grade (1000 × 1000, Python 3.12.10)

| Estrutura | MiB | Bytes por célula |
|---|---|---|
| lista de listas (criar_grade) | 8.45 | 8.86 |
| cópia com deepcopy | 8.45 | 8.86 |
| grade nova devolvida por proxima_geracao | 8.45 | 8.86 |
| pico durante proxima_geracao | 8.52 | 8.94 |
| vetor de bytes com moldura (refatorada) | 0.99 | 1.04 |

Os valores são relativos ao que já estava alocado antes de cada medida; o pico de `proxima_geracao` não inclui a grade de entrada, que continua viva durante a chamada.
