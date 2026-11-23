# Tabelas dos experimentos

Gerado por `python -m experimentos.analisar`. Tempos em segundos, mediana das repetições.

## Equivalência das versões

✅ Todas as versões produziram **a mesma grade final** em todas as execuções (grades 1000×1000). O experimento também vale como teste de equivalência em escala.

## Tempo por configuração — grade 1000 x 1000

| Versão | *workers* | Mediana (s) | Desvio (s) | Total (s) | Speedup vs prof. | Speedup do laço | Speedup total | Efic. do laço | Efic. total | Karp–Flatt | Amdahl 1/f | Gustafson S' |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sequencial (professor) | 1 | 14.4024 | 0.3580 | 14.4024 | 1.00 | 0.31 | 0.31 | 0.313 | 0.313 | — | — | — |
| Sequencial (refatorada) | 1 | 4.5027 | 0.1800 | 4.5027 | 3.20 | 1.00 | 1.00 | 1.000 | 1.000 | — | — | — |
| Paralela (processos) | 1 | 4.7561 | 0.1399 | 4.8108 | 3.03 | 0.95 | 0.94 | 0.947 | 0.936 | — | — | — |
| Paralela (processos) | 2 | 2.5412 | 0.0243 | 2.6059 | 5.67 | 1.77 | 1.73 | 0.886 | 0.864 | 0.129 | 7.77 | 1.87 |
| Paralela (processos) | 4 | 1.5735 | 0.0448 | 1.6464 | 9.15 | 2.86 | 2.73 | 0.715 | 0.684 | 0.133 | 7.54 | 3.60 |
| Paralela (processos) | 8 | 1.2247 | 0.0168 | 1.3316 | 11.76 | 3.68 | 3.38 | 0.460 | 0.423 | 0.168 | 5.95 | 6.82 |
| Paralela (processos) | 12 | 1.0104 | 0.0190 | 1.1400 | 14.25 | 4.46 | 3.95 | 0.371 | 0.329 | 0.154 | 6.50 | 10.31 |
| Paralela (processos) | 16 | 1.0185 | 0.0406 | 1.1818 | 14.14 | 4.42 | 3.81 | 0.276 | 0.238 | 0.175 | 5.73 | 13.38 |
| Paralela (threads) | 1 | 4.8077 | 0.0632 | 4.8082 | 3.00 | 0.94 | 0.94 | 0.937 | 0.936 | — | — | — |
| Paralela (threads) | 2 | 4.5512 | 0.0390 | 4.5526 | 3.16 | 0.99 | 0.99 | 0.495 | 0.494 | 1.022 | 0.98 | 0.98 |
| Paralela (threads) | 4 | 4.6247 | 0.0465 | 4.6259 | 3.11 | 0.97 | 0.97 | 0.243 | 0.243 | 1.036 | 0.97 | 0.89 |
| Paralela (threads) | 8 | 4.8455 | 0.0873 | 4.8482 | 2.97 | 0.93 | 0.93 | 0.116 | 0.116 | 1.087 | 0.92 | 0.39 |
| Paralela (threads) | 12 | 4.9120 | 0.0186 | 4.9138 | 2.93 | 0.92 | 0.92 | 0.076 | 0.076 | 1.099 | 0.91 | -0.09 |
| Paralela (threads) | 16 | 5.1438 | 0.1518 | 5.1477 | 2.80 | 0.88 | 0.87 | 0.055 | 0.055 | 1.152 | 0.87 | -1.28 |
| Distribuída (localhost) | 1 | 4.8235 | 0.0096 | 4.8266 | 2.99 | 0.93 | 0.93 | 0.933 | 0.933 | — | — | — |
| Distribuída (localhost) | 2 | 2.6434 | 0.1754 | 2.6466 | 5.45 | 1.70 | 1.70 | 0.852 | 0.851 | 0.174 | 5.74 | 1.83 |
| Distribuída (localhost) | 4 | 1.5808 | 0.0459 | 1.5833 | 9.11 | 2.85 | 2.84 | 0.712 | 0.711 | 0.135 | 7.42 | 3.60 |
| Distribuída (localhost) | 8 | 1.2536 | 0.0334 | 1.2572 | 11.49 | 3.59 | 3.58 | 0.449 | 0.448 | 0.175 | 5.70 | 6.77 |
| Distribuída (localhost) | 12 | 0.9880 | 0.0328 | 0.9917 | 14.58 | 4.56 | 4.54 | 0.380 | 0.378 | 0.148 | 6.74 | 10.37 |
| Distribuída (localhost) | 16 | 1.0115 | 0.0450 | 1.0190 | 14.24 | 4.45 | 4.42 | 0.278 | 0.276 | 0.173 | 5.78 | 13.41 |
| Distribuída (borda em bits) | 1 | 4.9580 | 0.1163 | 4.9614 | 2.90 | 0.91 | 0.91 | 0.908 | 0.907 | — | — | — |
| Distribuída (borda em bits) | 2 | 2.6359 | 0.0496 | 2.6384 | 5.46 | 1.71 | 1.71 | 0.854 | 0.853 | 0.171 | 5.85 | 1.83 |
| Distribuída (borda em bits) | 4 | 1.6048 | 0.0744 | 1.6069 | 8.97 | 2.81 | 2.80 | 0.701 | 0.701 | 0.142 | 7.05 | 3.57 |
| Distribuída (borda em bits) | 8 | 1.2527 | 0.0154 | 1.2550 | 11.50 | 3.59 | 3.59 | 0.449 | 0.449 | 0.175 | 5.71 | 6.77 |
| Distribuída (borda em bits) | 12 | 1.0088 | 0.0355 | 1.0132 | 14.28 | 4.46 | 4.44 | 0.372 | 0.370 | 0.153 | 6.51 | 10.31 |
| Distribuída (borda em bits) | 16 | 1.0694 | 0.0513 | 1.0799 | 13.47 | 4.21 | 4.17 | 0.263 | 0.261 | 0.187 | 5.36 | 13.20 |

**Speedup/eficiência do laço** usam só o tempo das gerações; **total** inclui criar processos e abrir conexões — é ele que mostra o custo de inicialização, que doi mais nas grades pequenas.

— = não se aplica. Karp–Flatt negativo com `1/f` vazio significa **speedup superlinear** ($S_p > p$), típico de efeito de cache quando a faixa de cada worker passa a caber no cache; nesse caso as leis de Amdahl e Gustafson não têm sentido físico e são omitidas.

## Impacto das melhorias (1 trabalhador)

| Grade | Versão | Mediana (s) | Ganho vs professor (×) |
|---|---|---|---|
| 1000 | Sequencial (professor) | 14.4024 | 1.00 |
| 1000 | Sequencial (refatorada) | 4.5027 | 3.20 |
| 1000 | Paralela (processos) | 4.7561 | 3.03 |
| 1000 | Paralela (threads) | 4.8077 | 3.00 |
| 1000 | Distribuída (localhost) | 4.8235 | 2.99 |
| 1000 | Distribuída (borda em bits) | 4.9580 | 2.90 |
