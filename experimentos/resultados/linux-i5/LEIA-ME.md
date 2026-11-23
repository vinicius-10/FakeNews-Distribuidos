# Medições no notebook com Linux (i5-1240P)

Bateria do `medir.py` rodada no notebook do João, em **Linux nativo** (Fedora 44), para comparar
com as medições do PC do grupo (Windows, i9-12900F) que estão em `../`. As duas máquinas e os dois
sistemas **não se misturam** num mesmo gráfico de *speedup*: cada uma tem a sua tabela.

| Item | Valor |
|---|---|
| Processador | Intel Core i5-1240P: 12 núcleos (4 P com *hyper-threading* + 8 E), 16 lógicos |
| Memória | 15,3 GB |
| Sistema | Fedora Linux 44, kernel 7.3.3 |
| Python | 3.12.16 (CPython) |
| Condição | notebook na tomada, governador de CPU `performance`; distribuída em `localhost` |
| Código | `main` em `ec05145` (depois do PR #9) |

Comando (rodado numa cópia do repositório, para não sobrescrever o `ambiente.csv` do PC do grupo):

```
python3.12 -m experimentos.medir --tamanhos 1000 --workers 1 2 4 8 12 16 --repeticoes 5 \
    --aquecimento 1 --cpu "12th Gen Intel(R) Core(TM) i5-1240P" --nucleos-fisicos 12 \
    --ambiente "notebook na tomada, governador performance, Fedora Linux nativo; ..." \
    --saida experimentos/resultados/medicoes_linux_i5.csv
python3.12 -m experimentos.analisar --csv experimentos/resultados/medicoes_linux_i5.csv \
    --saida linux_analise --sem-graficos
```

1000 × 1000, 20 gerações, 5% de espalhadores, limiar 2, 1 aquecimento + 5 repetições, mediana.
130 medições em 528 s, **todas com a mesma grade final** (SHA-256).

| Arquivo | O que tem |
|---|---|
| `medicoes.csv` | uma linha por repetição (formato do `medir.py`) |
| `tabelas.md`, `resumo.csv` | saída do `analisar.py` |
| `ambiente.csv` | máquina; a memória foi preenchida de `/proc/meminfo`, porque o `psutil` não está instalado |

Sem gráficos: o `matplotlib` não está instalado nesta máquina.
