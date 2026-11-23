# Bateria de experimentos — resumo

Mediana do tempo do laço por configuração. Speedup contra a `sequencial` do mesmo cenário.

## p0.01_l1_300x300

- percentual de espalhadores: **1.00%**
- limiar: **1**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.1998 | 0.0018 | 1.01 | 1.01 | 20 |
| `distribuida_bits` | 2 | 0.1068 | 0.0016 | 1.90 | 0.95 | 20 |
| `distribuida_bits` | 4 | 0.0598 | 0.0032 | 3.39 | 0.85 | 20 |
| `distribuida_local` | 1 | 0.2008 | 0.0016 | 1.01 | 1.01 | 20 |
| `distribuida_local` | 2 | 0.1051 | 0.0004 | 1.93 | 0.96 | 20 |
| `distribuida_local` | 4 | 0.0617 | 0.0043 | 3.28 | 0.82 | 20 |
| `paralela_processos` | 1 | 0.2044 | 0.0021 | 0.99 | 0.99 | 20 |
| `paralela_processos` | 2 | 0.1069 | 0.0011 | 1.90 | 0.95 | 20 |
| `paralela_processos` | 4 | 0.0637 | 0.0043 | 3.18 | 0.80 | 20 |
| `paralela_threads` | 1 | 0.2449 | 0.0201 | 0.83 | 0.83 | 20 |
| `paralela_threads` | 2 | 0.2683 | 0.0191 | 0.76 | 0.38 | 20 |
| `paralela_threads` | 4 | 0.2527 | 0.0145 | 0.80 | 0.20 | 20 |
| `sequencial` | 1 | 0.2026 | 0.0020 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.01_l1_600x600

- percentual de espalhadores: **1.00%**
- limiar: **1**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.8118 | 0.0008 | 1.28 | 1.28 | 20 |
| `distribuida_bits` | 2 | 0.4223 | 0.0035 | 2.46 | 1.23 | 20 |
| `distribuida_bits` | 4 | 0.2245 | 0.0100 | 4.62 | 1.16 | 20 |
| `distribuida_local` | 1 | 0.8142 | 0.0030 | 1.28 | 1.28 | 20 |
| `distribuida_local` | 2 | 0.4165 | 0.0055 | 2.49 | 1.25 | 20 |
| `distribuida_local` | 4 | 0.2278 | 0.0074 | 4.56 | 1.14 | 20 |
| `paralela_processos` | 1 | 0.8403 | 0.0119 | 1.24 | 1.24 | 20 |
| `paralela_processos` | 2 | 0.4381 | 0.0345 | 2.37 | 1.19 | 20 |
| `paralela_processos` | 4 | 0.2176 | 0.0044 | 4.77 | 1.19 | 20 |
| `paralela_threads` | 1 | 0.9825 | 0.0506 | 1.06 | 1.06 | 20 |
| `paralela_threads` | 2 | 0.9961 | 0.0358 | 1.04 | 0.52 | 20 |
| `paralela_threads` | 4 | 0.9752 | 0.0624 | 1.06 | 0.27 | 20 |
| `sequencial` | 1 | 1.0383 | 0.1931 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.01_l2_300x300

- percentual de espalhadores: **1.00%**
- limiar: **2**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.5540 | 0.0097 | 1.10 | 1.10 | 20 |
| `distribuida_bits` | 2 | 0.2802 | 0.0043 | 2.17 | 1.08 | 20 |
| `distribuida_bits` | 4 | 0.1476 | 0.0016 | 4.11 | 1.03 | 20 |
| `distribuida_local` | 1 | 0.5468 | 0.0017 | 1.11 | 1.11 | 20 |
| `distribuida_local` | 2 | 0.2817 | 0.0018 | 2.16 | 1.08 | 20 |
| `distribuida_local` | 4 | 0.1472 | 0.0050 | 4.12 | 1.03 | 20 |
| `paralela_processos` | 1 | 0.5308 | 0.0047 | 1.14 | 1.14 | 20 |
| `paralela_processos` | 2 | 0.2737 | 0.0019 | 2.22 | 1.11 | 20 |
| `paralela_processos` | 4 | 0.1434 | 0.0021 | 4.23 | 1.06 | 20 |
| `paralela_threads` | 1 | 0.6347 | 0.0192 | 0.96 | 0.96 | 20 |
| `paralela_threads` | 2 | 0.6559 | 0.0437 | 0.93 | 0.46 | 20 |
| `paralela_threads` | 4 | 0.6433 | 0.0170 | 0.94 | 0.24 | 20 |
| `sequencial` | 1 | 0.6073 | 0.0462 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.01_l2_600x600

- percentual de espalhadores: **1.00%**
- limiar: **2**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 2.0784 | 0.0137 | 1.32 | 1.32 | 20 |
| `distribuida_bits` | 2 | 1.0414 | 0.0117 | 2.64 | 1.32 | 20 |
| `distribuida_bits` | 4 | 0.5695 | 0.0328 | 4.82 | 1.21 | 20 |
| `distribuida_local` | 1 | 2.0920 | 0.0132 | 1.31 | 1.31 | 20 |
| `distribuida_local` | 2 | 1.0675 | 0.0149 | 2.57 | 1.29 | 20 |
| `distribuida_local` | 4 | 0.5513 | 0.0105 | 4.98 | 1.25 | 20 |
| `paralela_processos` | 1 | 2.1039 | 0.0148 | 1.31 | 1.31 | 20 |
| `paralela_processos` | 2 | 1.0643 | 0.0263 | 2.58 | 1.29 | 20 |
| `paralela_processos` | 4 | 0.5731 | 0.0177 | 4.79 | 1.20 | 20 |
| `paralela_threads` | 1 | 2.6748 | 0.1145 | 1.03 | 1.03 | 20 |
| `paralela_threads` | 2 | 2.7488 | 0.0855 | 1.00 | 0.50 | 20 |
| `paralela_threads` | 4 | 3.1148 | 0.2160 | 0.88 | 0.22 | 20 |
| `sequencial` | 1 | 2.7462 | 0.2326 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.01_l3_300x300

- percentual de espalhadores: **1.00%**
- limiar: **3**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.0529 | 0.0019 | 1.20 | 1.20 | 2 |
| `distribuida_bits` | 2 | 0.0269 | 0.0004 | 2.36 | 1.18 | 2 |
| `distribuida_bits` | 4 | 0.0142 | 0.0003 | 4.47 | 1.12 | 2 |
| `distribuida_local` | 1 | 0.0520 | 0.0002 | 1.22 | 1.22 | 2 |
| `distribuida_local` | 2 | 0.0273 | 0.0006 | 2.32 | 1.16 | 2 |
| `distribuida_local` | 4 | 0.0140 | 0.0001 | 4.53 | 1.13 | 2 |
| `paralela_processos` | 1 | 0.0534 | 0.0007 | 1.19 | 1.19 | 2 |
| `paralela_processos` | 2 | 0.0272 | 0.0032 | 2.33 | 1.16 | 2 |
| `paralela_processos` | 4 | 0.0144 | 0.0008 | 4.41 | 1.10 | 2 |
| `paralela_threads` | 1 | 0.0818 | 0.0108 | 0.77 | 0.77 | 2 |
| `paralela_threads` | 2 | 0.0643 | 0.0225 | 0.99 | 0.49 | 2 |
| `paralela_threads` | 4 | 0.0957 | 0.0183 | 0.66 | 0.17 | 2 |
| `sequencial` | 1 | 0.0633 | 0.0138 | 1.00 | 1.00 | 2 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.01_l3_600x600

- percentual de espalhadores: **1.00%**
- limiar: **3**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.2199 | 0.0047 | 1.23 | 1.23 | 2 |
| `distribuida_bits` | 2 | 0.1122 | 0.0032 | 2.42 | 1.21 | 2 |
| `distribuida_bits` | 4 | 0.0575 | 0.0007 | 4.71 | 1.18 | 2 |
| `distribuida_local` | 1 | 0.2142 | 0.0148 | 1.27 | 1.27 | 2 |
| `distribuida_local` | 2 | 0.1090 | 0.0005 | 2.49 | 1.24 | 2 |
| `distribuida_local` | 4 | 0.0558 | 0.0007 | 4.86 | 1.21 | 2 |
| `paralela_processos` | 1 | 0.2143 | 0.0053 | 1.26 | 1.26 | 2 |
| `paralela_processos` | 2 | 0.1063 | 0.0014 | 2.55 | 1.28 | 2 |
| `paralela_processos` | 4 | 0.0613 | 0.0043 | 4.42 | 1.11 | 2 |
| `paralela_threads` | 1 | 0.3327 | 0.0221 | 0.81 | 0.81 | 2 |
| `paralela_threads` | 2 | 0.3365 | 0.0626 | 0.81 | 0.40 | 2 |
| `paralela_threads` | 4 | 0.3218 | 0.0525 | 0.84 | 0.21 | 2 |
| `sequencial` | 1 | 0.2711 | 0.0247 | 1.00 | 1.00 | 2 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l1_300x300

- percentual de espalhadores: **5.00%**
- limiar: **1**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.0931 | 0.0008 | 1.04 | 1.04 | 9 |
| `distribuida_bits` | 2 | 0.0491 | 0.0005 | 1.97 | 0.98 | 9 |
| `distribuida_bits` | 4 | 0.0264 | 0.0015 | 3.66 | 0.91 | 9 |
| `distribuida_local` | 1 | 0.0914 | 0.0009 | 1.06 | 1.06 | 9 |
| `distribuida_local` | 2 | 0.0483 | 0.0006 | 2.00 | 1.00 | 9 |
| `distribuida_local` | 4 | 0.0272 | 0.0060 | 3.56 | 0.89 | 9 |
| `paralela_processos` | 1 | 0.0935 | 0.0004 | 1.03 | 1.03 | 9 |
| `paralela_processos` | 2 | 0.0494 | 0.0009 | 1.96 | 0.98 | 9 |
| `paralela_processos` | 4 | 0.0261 | 0.0005 | 3.71 | 0.93 | 9 |
| `paralela_threads` | 1 | 0.1083 | 0.0169 | 0.89 | 0.89 | 9 |
| `paralela_threads` | 2 | 0.1094 | 0.0286 | 0.88 | 0.44 | 9 |
| `paralela_threads` | 4 | 0.1036 | 0.0032 | 0.93 | 0.23 | 9 |
| `sequencial` | 1 | 0.0967 | 0.0031 | 1.00 | 1.00 | 9 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l1_600x600

- percentual de espalhadores: **5.00%**
- limiar: **1**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.3712 | 0.0029 | 1.32 | 1.32 | 9 |
| `distribuida_bits` | 2 | 0.1909 | 0.0004 | 2.57 | 1.28 | 9 |
| `distribuida_bits` | 4 | 0.1021 | 0.0022 | 4.80 | 1.20 | 9 |
| `distribuida_local` | 1 | 0.3764 | 0.0033 | 1.30 | 1.30 | 9 |
| `distribuida_local` | 2 | 0.1886 | 0.0002 | 2.60 | 1.30 | 9 |
| `distribuida_local` | 4 | 0.0986 | 0.0007 | 4.97 | 1.24 | 9 |
| `paralela_processos` | 1 | 0.3742 | 0.0015 | 1.31 | 1.31 | 9 |
| `paralela_processos` | 2 | 0.1900 | 0.0023 | 2.58 | 1.29 | 9 |
| `paralela_processos` | 4 | 0.1004 | 0.0020 | 4.88 | 1.22 | 9 |
| `paralela_threads` | 1 | 0.4729 | 0.0324 | 1.04 | 1.04 | 9 |
| `paralela_threads` | 2 | 0.4969 | 0.0370 | 0.99 | 0.49 | 9 |
| `paralela_threads` | 4 | 0.4787 | 0.0296 | 1.02 | 0.26 | 9 |
| `sequencial` | 1 | 0.4901 | 0.0356 | 1.00 | 1.00 | 9 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l2_300x300

- percentual de espalhadores: **5.00%**
- limiar: **2**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.3675 | 0.0065 | 1.29 | 1.29 | 20 |
| `distribuida_bits` | 2 | 0.1871 | 0.0023 | 2.52 | 1.26 | 20 |
| `distribuida_bits` | 4 | 0.1016 | 0.0043 | 4.65 | 1.16 | 20 |
| `distribuida_local` | 1 | 0.3685 | 0.0008 | 1.28 | 1.28 | 20 |
| `distribuida_local` | 2 | 0.1886 | 0.0053 | 2.50 | 1.25 | 20 |
| `distribuida_local` | 4 | 0.1004 | 0.0014 | 4.70 | 1.18 | 20 |
| `paralela_processos` | 1 | 0.3772 | 0.0033 | 1.25 | 1.25 | 20 |
| `paralela_processos` | 2 | 0.1939 | 0.0007 | 2.44 | 1.22 | 20 |
| `paralela_processos` | 4 | 0.1010 | 0.0023 | 4.67 | 1.17 | 20 |
| `paralela_threads` | 1 | 0.4990 | 0.0490 | 0.95 | 0.95 | 20 |
| `paralela_threads` | 2 | 0.4581 | 0.0251 | 1.03 | 0.52 | 20 |
| `paralela_threads` | 4 | 0.4444 | 0.0040 | 1.06 | 0.27 | 20 |
| `sequencial` | 1 | 0.4723 | 0.0172 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l2_600x600

- percentual de espalhadores: **5.00%**
- limiar: **2**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 1.5137 | 0.0199 | 1.11 | 1.11 | 20 |
| `distribuida_bits` | 2 | 0.7755 | 0.0513 | 2.16 | 1.08 | 20 |
| `distribuida_bits` | 4 | 0.4069 | 0.0089 | 4.12 | 1.03 | 20 |
| `distribuida_local` | 1 | 1.5217 | 0.0084 | 1.10 | 1.10 | 20 |
| `distribuida_local` | 2 | 0.7774 | 0.0049 | 2.15 | 1.08 | 20 |
| `distribuida_local` | 4 | 0.3972 | 0.0009 | 4.22 | 1.05 | 20 |
| `paralela_processos` | 1 | 1.4873 | 0.0264 | 1.13 | 1.13 | 20 |
| `paralela_processos` | 2 | 0.7690 | 0.0050 | 2.18 | 1.09 | 20 |
| `paralela_processos` | 4 | 0.3917 | 0.0228 | 4.28 | 1.07 | 20 |
| `paralela_threads` | 1 | 1.7763 | 0.0583 | 0.94 | 0.94 | 20 |
| `paralela_threads` | 2 | 1.7626 | 0.0609 | 0.95 | 0.48 | 20 |
| `paralela_threads` | 4 | 1.8109 | 0.0397 | 0.92 | 0.23 | 20 |
| `sequencial` | 1 | 1.6747 | 0.0388 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l3_300x300

- percentual de espalhadores: **5.00%**
- limiar: **3**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.0765 | 0.0015 | 1.08 | 1.08 | 3 |
| `distribuida_bits` | 2 | 0.0414 | 0.0025 | 1.99 | 0.99 | 3 |
| `distribuida_bits` | 4 | 0.0208 | 0.0002 | 3.96 | 0.99 | 3 |
| `distribuida_local` | 1 | 0.0780 | 0.0010 | 1.05 | 1.05 | 3 |
| `distribuida_local` | 2 | 0.0404 | 0.0005 | 2.03 | 1.02 | 3 |
| `distribuida_local` | 4 | 0.0204 | 0.0011 | 4.04 | 1.01 | 3 |
| `paralela_processos` | 1 | 0.0772 | 0.0013 | 1.07 | 1.07 | 3 |
| `paralela_processos` | 2 | 0.0393 | 0.0003 | 2.09 | 1.05 | 3 |
| `paralela_processos` | 4 | 0.0209 | 0.0009 | 3.94 | 0.98 | 3 |
| `paralela_threads` | 1 | 0.1377 | 0.0299 | 0.60 | 0.60 | 3 |
| `paralela_threads` | 2 | 0.1130 | 0.0181 | 0.73 | 0.36 | 3 |
| `paralela_threads` | 4 | 0.0937 | 0.0259 | 0.88 | 0.22 | 3 |
| `sequencial` | 1 | 0.0823 | 0.0062 | 1.00 | 1.00 | 3 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.05_l3_600x600

- percentual de espalhadores: **5.00%**
- limiar: **3**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.3139 | 0.0021 | 1.32 | 1.32 | 3 |
| `distribuida_bits` | 2 | 0.1595 | 0.0016 | 2.59 | 1.29 | 3 |
| `distribuida_bits` | 4 | 0.0822 | 0.0027 | 5.02 | 1.26 | 3 |
| `distribuida_local` | 1 | 0.3132 | 0.0019 | 1.32 | 1.32 | 3 |
| `distribuida_local` | 2 | 0.1605 | 0.0053 | 2.57 | 1.29 | 3 |
| `distribuida_local` | 4 | 0.0828 | 0.0052 | 4.99 | 1.25 | 3 |
| `paralela_processos` | 1 | 0.3136 | 0.0041 | 1.32 | 1.32 | 3 |
| `paralela_processos` | 2 | 0.1631 | 0.0038 | 2.53 | 1.27 | 3 |
| `paralela_processos` | 4 | 0.0874 | 0.0054 | 4.73 | 1.18 | 3 |
| `paralela_threads` | 1 | 0.4129 | 0.0397 | 1.00 | 1.00 | 3 |
| `paralela_threads` | 2 | 0.4532 | 0.0156 | 0.91 | 0.46 | 3 |
| `paralela_threads` | 4 | 0.3955 | 0.0214 | 1.04 | 0.26 | 3 |
| `sequencial` | 1 | 0.4128 | 0.0293 | 1.00 | 1.00 | 3 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l1_300x300

- percentual de espalhadores: **10.00%**
- limiar: **1**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.0683 | 0.0026 | 1.23 | 1.23 | 7 |
| `distribuida_bits` | 2 | 0.0366 | 0.0018 | 2.29 | 1.14 | 7 |
| `distribuida_bits` | 4 | 0.0199 | 0.0004 | 4.22 | 1.06 | 7 |
| `distribuida_local` | 1 | 0.0691 | 0.0008 | 1.21 | 1.21 | 7 |
| `distribuida_local` | 2 | 0.0351 | 0.0001 | 2.39 | 1.20 | 7 |
| `distribuida_local` | 4 | 0.0196 | 0.0005 | 4.27 | 1.07 | 7 |
| `paralela_processos` | 1 | 0.0682 | 0.0004 | 1.23 | 1.23 | 7 |
| `paralela_processos` | 2 | 0.0358 | 0.0018 | 2.34 | 1.17 | 7 |
| `paralela_processos` | 4 | 0.0193 | 0.0002 | 4.33 | 1.08 | 7 |
| `paralela_threads` | 1 | 0.0871 | 0.0153 | 0.96 | 0.96 | 7 |
| `paralela_threads` | 2 | 0.0978 | 0.0168 | 0.86 | 0.43 | 7 |
| `paralela_threads` | 4 | 0.0834 | 0.0078 | 1.01 | 0.25 | 7 |
| `sequencial` | 1 | 0.0838 | 0.0121 | 1.00 | 1.00 | 7 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l1_600x600

- percentual de espalhadores: **10.00%**
- limiar: **1**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.2810 | 0.0094 | 1.20 | 1.20 | 7 |
| `distribuida_bits` | 2 | 0.1403 | 0.0026 | 2.40 | 1.20 | 7 |
| `distribuida_bits` | 4 | 0.0738 | 0.0017 | 4.57 | 1.14 | 7 |
| `distribuida_local` | 1 | 0.2761 | 0.0037 | 1.22 | 1.22 | 7 |
| `distribuida_local` | 2 | 0.1414 | 0.0113 | 2.38 | 1.19 | 7 |
| `distribuida_local` | 4 | 0.0752 | 0.0028 | 4.48 | 1.12 | 7 |
| `paralela_processos` | 1 | 0.2796 | 0.0030 | 1.20 | 1.20 | 7 |
| `paralela_processos` | 2 | 0.1384 | 0.0010 | 2.43 | 1.22 | 7 |
| `paralela_processos` | 4 | 0.0745 | 0.0023 | 4.52 | 1.13 | 7 |
| `paralela_threads` | 1 | 0.3549 | 0.0230 | 0.95 | 0.95 | 7 |
| `paralela_threads` | 2 | 0.3193 | 0.0208 | 1.05 | 0.53 | 7 |
| `paralela_threads` | 4 | 0.3229 | 0.0100 | 1.04 | 0.26 | 7 |
| `sequencial` | 1 | 0.3369 | 0.0089 | 1.00 | 1.00 | 7 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l2_300x300

- percentual de espalhadores: **10.00%**
- limiar: **2**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.2244 | 0.0012 | 1.30 | 1.30 | 20 |
| `distribuida_bits` | 2 | 0.1155 | 0.0023 | 2.51 | 1.26 | 20 |
| `distribuida_bits` | 4 | 0.0660 | 0.0025 | 4.40 | 1.10 | 20 |
| `distribuida_local` | 1 | 0.2225 | 0.0064 | 1.31 | 1.31 | 20 |
| `distribuida_local` | 2 | 0.1148 | 0.0053 | 2.53 | 1.27 | 20 |
| `distribuida_local` | 4 | 0.0652 | 0.0021 | 4.46 | 1.11 | 20 |
| `paralela_processos` | 1 | 0.2209 | 0.0023 | 1.32 | 1.32 | 20 |
| `paralela_processos` | 2 | 0.1134 | 0.0028 | 2.56 | 1.28 | 20 |
| `paralela_processos` | 4 | 0.0603 | 0.0025 | 4.82 | 1.21 | 20 |
| `paralela_threads` | 1 | 0.3266 | 0.0282 | 0.89 | 0.89 | 20 |
| `paralela_threads` | 2 | 0.2533 | 0.0107 | 1.15 | 0.57 | 20 |
| `paralela_threads` | 4 | 0.2429 | 0.0207 | 1.20 | 0.30 | 20 |
| `sequencial` | 1 | 0.2906 | 0.0302 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l2_600x600

- percentual de espalhadores: **10.00%**
- limiar: **2**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.8831 | 0.0183 | 1.33 | 1.33 | 20 |
| `distribuida_bits` | 2 | 0.4499 | 0.0070 | 2.60 | 1.30 | 20 |
| `distribuida_bits` | 4 | 0.2409 | 0.0062 | 4.86 | 1.21 | 20 |
| `distribuida_local` | 1 | 0.8669 | 0.0029 | 1.35 | 1.35 | 20 |
| `distribuida_local` | 2 | 0.4451 | 0.0163 | 2.63 | 1.31 | 20 |
| `distribuida_local` | 4 | 0.2312 | 0.0015 | 5.06 | 1.27 | 20 |
| `paralela_processos` | 1 | 0.8657 | 0.0128 | 1.35 | 1.35 | 20 |
| `paralela_processos` | 2 | 0.4354 | 0.0056 | 2.69 | 1.34 | 20 |
| `paralela_processos` | 4 | 0.2264 | 0.0051 | 5.17 | 1.29 | 20 |
| `paralela_threads` | 1 | 1.0993 | 0.0576 | 1.06 | 1.06 | 20 |
| `paralela_threads` | 2 | 1.1518 | 0.0776 | 1.02 | 0.51 | 20 |
| `paralela_threads` | 4 | 1.1764 | 0.0771 | 1.00 | 0.25 | 20 |
| `sequencial` | 1 | 1.1706 | 0.0419 | 1.00 | 1.00 | 20 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l3_300x300

- percentual de espalhadores: **10.00%**
- limiar: **3**
- grade: **300 × 300**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.1017 | 0.0029 | 1.14 | 1.14 | 4 |
| `distribuida_bits` | 2 | 0.0515 | 0.0008 | 2.25 | 1.13 | 4 |
| `distribuida_bits` | 4 | 0.0288 | 0.0019 | 4.04 | 1.01 | 4 |
| `distribuida_local` | 1 | 0.1115 | 0.0089 | 1.04 | 1.04 | 4 |
| `distribuida_local` | 2 | 0.0511 | 0.0033 | 2.27 | 1.14 | 4 |
| `distribuida_local` | 4 | 0.0267 | 0.0001 | 4.36 | 1.09 | 4 |
| `paralela_processos` | 1 | 0.0967 | 0.0011 | 1.20 | 1.20 | 4 |
| `paralela_processos` | 2 | 0.0513 | 0.0009 | 2.26 | 1.13 | 4 |
| `paralela_processos` | 4 | 0.0279 | 0.0038 | 4.17 | 1.04 | 4 |
| `paralela_threads` | 1 | 0.1245 | 0.0124 | 0.93 | 0.93 | 4 |
| `paralela_threads` | 2 | 0.1187 | 0.0100 | 0.98 | 0.49 | 4 |
| `paralela_threads` | 4 | 0.1173 | 0.0281 | 0.99 | 0.25 | 4 |
| `sequencial` | 1 | 0.1162 | 0.0031 | 1.00 | 1.00 | 4 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## p0.1_l3_600x600

- percentual de espalhadores: **10.00%**
- limiar: **3**
- grade: **600 × 600**

| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |
|---|---:|---:|---:|---:|---:|---:|
| `distribuida_bits` | 1 | 0.4005 | 0.0048 | 1.29 | 1.29 | 4 |
| `distribuida_bits` | 2 | 0.2105 | 0.0040 | 2.46 | 1.23 | 4 |
| `distribuida_bits` | 4 | 0.1072 | 0.0125 | 4.83 | 1.21 | 4 |
| `distribuida_local` | 1 | 0.4067 | 0.0094 | 1.27 | 1.27 | 4 |
| `distribuida_local` | 2 | 0.2036 | 0.0105 | 2.54 | 1.27 | 4 |
| `distribuida_local` | 4 | 0.1067 | 0.0043 | 4.85 | 1.21 | 4 |
| `paralela_processos` | 1 | 0.3971 | 0.0039 | 1.30 | 1.30 | 4 |
| `paralela_processos` | 2 | 0.2091 | 0.0108 | 2.48 | 1.24 | 4 |
| `paralela_processos` | 4 | 0.1205 | 0.0167 | 4.30 | 1.07 | 4 |
| `paralela_threads` | 1 | 0.5102 | 0.0566 | 1.01 | 1.01 | 4 |
| `paralela_threads` | 2 | 0.6273 | 0.0593 | 0.83 | 0.41 | 4 |
| `paralela_threads` | 4 | 0.5323 | 0.0368 | 0.97 | 0.24 | 4 |
| `sequencial` | 1 | 0.5176 | 0.0290 | 1.00 | 1.00 | 4 |

**Equivalência:** todas as versões produziram a mesma grade final. ✅

## Veredito geral

Todas as células fecharam com a mesma grade da sequencial — bateria válida para o relatório.

> `tempo_laco` é a métrica comparável entre versões. O `tempo_total` da distribuída começa depois que os workers conectam, então não serve para comparar com a paralela.
