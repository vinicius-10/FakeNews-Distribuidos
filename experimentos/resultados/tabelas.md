# Tabelas dos experimentos

Gerado por `python -m experimentos.analisar`. Tempos em segundos, mediana das repetições.

## Equivalência das versões

✅ Todas as versões produziram **a mesma grade final** em todas as execuções (grades 500×500, 1000×1000, 2000×2000). O experimento também vale como teste de equivalência em escala.

## Tempo por configuração — grade 500 x 500

| Versão | *workers* | Mediana (s) | Desvio (s) | Total (s) | Speedup vs prof. | Speedup vs ref. | Eficiência | Karp–Flatt | Amdahl 1/f | Gustafson S' |
|---|---|---|---|---|---|---|---|---|---|---|
| Sequencial (professor) | 1 | 4.1600 | 0.0661 | 4.1600 | 1.00 | 0.28 | 0.283 | — | — | — |
| Sequencial (refatorada) | 1 | 1.1784 | 0.0231 | 1.1784 | 3.53 | 1.00 | 1.000 | — | — | — |

— = não se aplica. Karp–Flatt negativo com `1/f` vazio significa **speedup superlinear** ($S_p > p$), típico de efeito de cache quando a faixa de cada worker passa a caber no cache; nesse caso as leis de Amdahl e Gustafson não têm sentido físico e são omitidas.

## Tempo por configuração — grade 1000 x 1000

| Versão | *workers* | Mediana (s) | Desvio (s) | Total (s) | Speedup vs prof. | Speedup vs ref. | Eficiência | Karp–Flatt | Amdahl 1/f | Gustafson S' |
|---|---|---|---|---|---|---|---|---|---|---|
| Sequencial (professor) | 1 | 16.4572 | 0.3994 | 16.4572 | 1.00 | 0.30 | 0.300 | — | — | — |
| Sequencial (refatorada) | 1 | 4.9360 | 1.1366 | 4.9360 | 3.33 | 1.00 | 1.000 | — | — | — |
| Paralela (processos) | 1 | 4.9726 | 0.0317 | 5.1156 | 3.31 | 0.99 | 0.993 | — | — | — |
| Paralela (processos) | 2 | 2.2182 | 0.0372 | 2.3552 | 7.42 | 2.23 | 1.113 | -0.101 | — | — |
| Paralela (processos) | 4 | 1.1628 | 0.0329 | 1.3256 | 14.15 | 4.25 | 1.061 | -0.019 | — | — |
| Paralela (processos) | 8 | 0.7115 | 0.0126 | 0.9022 | 23.13 | 6.94 | 0.867 | 0.022 | 45.70 | 7.85 |
| Paralela (processos) | 16 | 0.5137 | 0.0072 | 0.8020 | 32.04 | 9.61 | 0.601 | 0.044 | 22.55 | 15.33 |
| Paralela (processos) | 24 | 0.4556 | 0.0169 | 0.8373 | 36.12 | 10.83 | 0.451 | 0.053 | 18.93 | 22.78 |
| Paralela (threads) | 1 | 5.2219 | 0.1052 | 5.2227 | 3.15 | 0.95 | 0.945 | — | — | — |
| Paralela (threads) | 2 | 5.6716 | 0.4039 | 5.6735 | 2.90 | 0.87 | 0.435 | 1.298 | 0.77 | 0.70 |
| Paralela (threads) | 4 | 5.1677 | 0.1067 | 5.1690 | 3.18 | 0.96 | 0.239 | 1.063 | 0.94 | 0.81 |
| Paralela (threads) | 8 | 5.3031 | 0.1896 | 5.3046 | 3.10 | 0.93 | 0.116 | 1.085 | 0.92 | 0.41 |
| Paralela (threads) | 16 | 5.1189 | 0.0608 | 5.1219 | 3.21 | 0.96 | 0.060 | 1.040 | 0.96 | 0.41 |
| Paralela (threads) | 24 | 5.0693 | 0.1028 | 5.0732 | 3.25 | 0.97 | 0.041 | 1.028 | 0.97 | 0.35 |
| Distribuída (localhost) | 1 | 4.9745 | 0.0739 | 5.1101 | 3.31 | 0.99 | 0.992 | — | — | — |
| Distribuída (localhost) | 2 | 2.1715 | 0.0168 | 2.2858 | 7.58 | 2.27 | 1.137 | -0.120 | — | — |
| Distribuída (localhost) | 4 | 1.1856 | 0.0079 | 1.3180 | 13.88 | 4.16 | 1.041 | -0.013 | — | — |
| Distribuída (localhost) | 8 | 0.7320 | 0.0222 | 0.8835 | 22.48 | 6.74 | 0.843 | 0.027 | 37.57 | 7.81 |
| Distribuída (localhost) | 16 | 0.5310 | 0.0082 | 0.7238 | 30.99 | 9.30 | 0.581 | 0.048 | 20.80 | 15.28 |
| Distribuída (localhost) | 24 | 0.4377 | 0.0407 | 0.7117 | 37.60 | 11.28 | 0.470 | 0.049 | 20.39 | 22.87 |
| Distribuída (borda em bits) | 1 | 5.1070 | 0.2297 | 5.2227 | 3.22 | 0.97 | 0.967 | — | — | — |
| Distribuída (borda em bits) | 2 | 2.1798 | 0.0289 | 2.2920 | 7.55 | 2.26 | 1.132 | -0.117 | — | — |
| Distribuída (borda em bits) | 4 | 1.2087 | 0.0215 | 1.3334 | 13.62 | 4.08 | 1.021 | -0.007 | — | — |
| Distribuída (borda em bits) | 8 | 0.7514 | 0.0199 | 0.8902 | 21.90 | 6.57 | 0.821 | 0.031 | 32.13 | 7.78 |
| Distribuída (borda em bits) | 16 | 0.5472 | 0.0128 | 0.7414 | 30.07 | 9.02 | 0.564 | 0.052 | 19.38 | 15.23 |
| Distribuída (borda em bits) | 24 | 0.4692 | 0.0220 | 0.7093 | 35.07 | 10.52 | 0.438 | 0.056 | 17.95 | 22.72 |

— = não se aplica. Karp–Flatt negativo com `1/f` vazio significa **speedup superlinear** ($S_p > p$), típico de efeito de cache quando a faixa de cada worker passa a caber no cache; nesse caso as leis de Amdahl e Gustafson não têm sentido físico e são omitidas.

## Tempo por configuração — grade 2000 x 2000

| Versão | *workers* | Mediana (s) | Desvio (s) | Total (s) | Speedup vs prof. | Speedup vs ref. | Eficiência | Karp–Flatt | Amdahl 1/f | Gustafson S' |
|---|---|---|---|---|---|---|---|---|---|---|
| Sequencial (professor) | 1 | 65.8837 | 1.8923 | 65.8837 | 1.00 | 0.30 | 0.297 | — | — | — |
| Sequencial (refatorada) | 1 | 19.5456 | 3.7674 | 19.5456 | 3.37 | 1.00 | 1.000 | — | — | — |
| Paralela (processos) | 1 | 23.0181 | 0.2125 | 23.1556 | 2.86 | 0.85 | 0.849 | — | — | — |
| Paralela (processos) | 2 | 11.8297 | 0.1291 | 11.9762 | 5.57 | 1.65 | 0.826 | 0.210 | 4.75 | 1.79 |
| Paralela (processos) | 4 | 5.6859 | 0.0890 | 5.8473 | 11.59 | 3.44 | 0.859 | 0.054 | 18.34 | 3.84 |
| Paralela (processos) | 8 | 2.7090 | 0.0420 | 2.9101 | 24.32 | 7.21 | 0.902 | 0.015 | 64.33 | 7.89 |
| Paralela (processos) | 16 | 1.9383 | 0.0296 | 2.2214 | 33.99 | 10.08 | 0.630 | 0.039 | 25.57 | 15.41 |
| Paralela (processos) | 24 | 1.7889 | 0.0344 | 2.1656 | 36.83 | 10.93 | 0.455 | 0.052 | 19.22 | 22.80 |
| Distribuída (localhost) | 1 | 20.0074 | 0.4351 | 20.3602 | 3.29 | 0.98 | 0.977 | — | — | — |
| Distribuída (localhost) | 2 | 9.3377 | 0.1942 | 9.5974 | 7.06 | 2.09 | 1.047 | -0.044 | — | — |
| Distribuída (localhost) | 4 | 4.9169 | 0.1116 | 5.2389 | 13.40 | 3.98 | 0.994 | 0.002 | 481.29 | 3.99 |
| Distribuída (localhost) | 8 | 2.5583 | 0.0319 | 2.8900 | 25.75 | 7.64 | 0.955 | 0.007 | 148.57 | 7.95 |
| Distribuída (localhost) | 16 | 1.8873 | 0.0226 | 2.2399 | 34.91 | 10.36 | 0.647 | 0.036 | 27.52 | 15.46 |
| Distribuída (localhost) | 24 | 1.6041 | 0.0159 | 2.0126 | 41.07 | 12.18 | 0.508 | 0.042 | 23.72 | 23.03 |
| Distribuída (borda em bits) | 1 | 20.9063 | 0.2946 | 21.1693 | 3.15 | 0.93 | 0.935 | — | — | — |
| Distribuída (borda em bits) | 2 | 9.6550 | 0.0860 | 9.9030 | 6.82 | 2.02 | 1.012 | -0.012 | — | — |
| Distribuída (borda em bits) | 4 | 4.9880 | 0.0769 | 5.3085 | 13.21 | 3.92 | 0.980 | 0.007 | 144.26 | 3.98 |
| Distribuída (borda em bits) | 8 | 2.5482 | 0.0271 | 2.9059 | 25.85 | 7.67 | 0.959 | 0.006 | 162.81 | 7.96 |
| Distribuída (borda em bits) | 16 | 1.8791 | 0.0231 | 2.2287 | 35.06 | 10.40 | 0.650 | 0.036 | 27.87 | 15.46 |
| Distribuída (borda em bits) | 24 | 1.6324 | 0.0361 | 2.0499 | 40.36 | 11.97 | 0.499 | 0.044 | 22.90 | 23.00 |

— = não se aplica. Karp–Flatt negativo com `1/f` vazio significa **speedup superlinear** ($S_p > p$), típico de efeito de cache quando a faixa de cada worker passa a caber no cache; nesse caso as leis de Amdahl e Gustafson não têm sentido físico e são omitidas.

## Impacto das melhorias (1 trabalhador)

| Grade | Versão | Mediana (s) | Ganho vs professor (×) |
|---|---|---|---|
| 500 | Sequencial (professor) | 4.1600 | 1.00 |
| 500 | Sequencial (refatorada) | 1.1784 | 3.53 |
| 1000 | Sequencial (professor) | 16.4572 | 1.00 |
| 1000 | Sequencial (refatorada) | 4.9360 | 3.33 |
| 1000 | Paralela (processos) | 4.9726 | 3.31 |
| 1000 | Paralela (threads) | 5.2219 | 3.15 |
| 1000 | Distribuída (localhost) | 4.9745 | 3.31 |
| 1000 | Distribuída (borda em bits) | 5.1070 | 3.22 |
| 2000 | Sequencial (professor) | 65.8837 | 1.00 |
| 2000 | Sequencial (refatorada) | 19.5456 | 3.37 |
| 2000 | Paralela (processos) | 23.0181 | 2.86 |
| 2000 | Distribuída (localhost) | 20.0074 | 3.29 |
| 2000 | Distribuída (borda em bits) | 20.9063 | 3.15 |
