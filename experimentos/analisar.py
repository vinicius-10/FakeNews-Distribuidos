"""
Análise das medições: tabelas, speedup, eficiência, Karp--Flatt e gráficos.

Lê `experimentos/resultados/medicoes.csv` (gerado por `medir.py`), usa a
**mediana** das repetições de cada configuração (regra do CONTRIBUTING) e
produz:

- `tabelas.md`: tabelas prontas para colar no relatório;
- `resumo.csv`: uma linha por configuração, com mediana, desvio, speedup,
  eficiência e fração serial de Karp--Flatt;
- gráficos `.png` em `resultados/graficos/` (precisa de `matplotlib`, que é
  opcional: sem ele as tabelas continuam sendo geradas).

Duas linhas de base
-------------------
- **Sequencial refatorada** (`sequencial`): é a base correta do *speedup* das
  versões paralela e distribuída, porque usa exatamente o mesmo núcleo de
  cálculo. Com 1 trabalhador o programa é o mesmo, só muda quem chama.
- **Sequencial do professor** (`sequencial_original`): serve para medir a
  melhoria "grade compacta" (troca do `deepcopy` por dois buffers de bytes).

Uso:
    python -m experimentos.analisar
    python -m experimentos.analisar --csv outro.csv --sem-graficos
"""

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "experimentos" / "resultados"


def _console_seguro():
    """
    Impede que um caractere fora da tabela do terminal derrube o script.

    No Windows o console costuma usar cp1252, que não tem símbolos como ✅/❌.
    Os arquivos (CSV e Markdown) são sempre gravados em UTF-8; só o terminal
    recebe "?" no lugar do símbolo que ele não sabe desenhar.
    """
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")

# Ordem em que as versões aparecem nas tabelas e nos gráficos.
ORDEM_VERSOES = ["sequencial_original", "sequencial", "paralela_processos",
                 "paralela_threads", "distribuida_local", "distribuida_bits"]

ROTULOS = {
    "sequencial_original": "Sequencial (professor)",
    "sequencial": "Sequencial (refatorada)",
    "paralela_processos": "Paralela (processos)",
    "paralela_threads": "Paralela (threads)",
    "distribuida_local": "Distribuída (localhost)",
    "distribuida_bits": "Distribuída (borda em bits)",
}

CORES = {
    "sequencial_original": "#8d99ae",
    "sequencial": "#2b2d42",
    "paralela_processos": "#0a9396",
    "paralela_threads": "#e07a5f",
    "distribuida_local": "#3d5a80",
    "distribuida_bits": "#9b5de5",
}

MARCADORES = {
    "sequencial_original": "s",
    "sequencial": "D",
    "paralela_processos": "o",
    "paralela_threads": "^",
    "distribuida_local": "v",
    "distribuida_bits": "P",
}


# ---------------------------------------------------------------------------
# Leitura e agregação
# ---------------------------------------------------------------------------

def carregar(caminho):
    """Lê o CSV de medições e converte os números."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for linha in linhas:
        for campo in ("tempo_laco_s", "tempo_total_s"):
            linha[campo] = float(linha[campo]) if linha[campo] else None
        for campo in ("workers", "linhas", "colunas", "geracoes_pedidas",
                      "geracoes_executadas", "limiar", "repeticao"):
            linha[campo] = int(linha[campo])
        linha["percentual"] = float(linha["percentual"])
    return linhas


def agrupar(linhas):
    """
    Agrupa por (versão, tamanho, workers) e calcula mediana e desvio.

    A mediana é a estatística usada na análise; o desvio padrão amostral serve
    para mostrar a variabilidade, como pede a metodologia de medição.
    """
    grupos = defaultdict(list)
    for linha in linhas:
        grupos[(linha["versao"], linha["linhas"], linha["workers"])].append(linha)
    resumo = {}
    for chave, medidas in grupos.items():
        tempos = [m["tempo_laco_s"] for m in medidas]
        totais = [m["tempo_total_s"] for m in medidas if m["tempo_total_s"] is not None]
        resumo[chave] = {
            "repeticao": len(tempos),
            "mediana": statistics.median(tempos),
            "desvio": statistics.stdev(tempos) if len(tempos) > 1 else 0.0,
            "minimo": min(tempos),
            "maximo": max(tempos),
            "mediana_total": statistics.median(totais) if totais else None,
            "linha": medidas[0],
        }
    return resumo


def verificar_equivalencia(linhas):
    """
    Confere se todas as versões produziram a mesma grade final.

    Para cada tamanho, compara o hash de cada execução com o da sequencial
    refatorada. Devolve (ok, lista de divergências, lista de tamanhos).
    """
    referencia = {}
    for linha in linhas:
        if linha["versao"] == "sequencial":
            referencia[linha["linhas"]] = linha["hash_grade"]
    divergencias = []
    for linha in linhas:
        esperado = referencia.get(linha["linhas"])
        if esperado is None:
            continue
        if linha["hash_grade"] != esperado:
            divergencias.append((linha["versao"], linha["linhas"], linha["workers"],
                                 linha["hash_grade"][:12], esperado[:12]))
    return not divergencias, divergencias, sorted(referencia)


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def speedup(t1, tp):
    """Speedup S_p = T_1 / T_p."""
    return t1 / tp if tp else float("nan")


def eficiencia(s, workers):
    """Eficiência E_p = S_p / p."""
    return s / workers if workers else float("nan")


def karp_flatt(s, workers):
    """
    Fração serial medida f = (1/S - 1/p) / (1 - 1/p)  (Karp e Flatt, 1990).

    f constante indica limite do programa; f crescendo com p indica custo de
    sincronização/comunicação; f irregular indica desbalanceamento de carga.
    """
    if workers <= 1:
        return None
    return (1.0 / s - 1.0 / workers) / (1.0 - 1.0 / workers)


def amdahl(f, workers):
    """
    Speedup previsto pela lei de Amdahl com fração serial f e p processadores.

    S(p) = 1 / (f + (1 - f)/p). O limite com p -> infinito é 1/f.
    """
    if f is None:
        return None
    return 1.0 / (f + (1.0 - f) / workers)


def gustafson(f, workers):
    """
    Speedup escalado (lei de Gustafson): S'(p) = p - f*(p - 1).

    Ao contrário de Amdahl, supõe que o problema cresce com o número de
    processadores — é o que a escalabilidade fraca mede.
    """
    if f is None:
        return None
    return workers - f * (workers - 1)


def montar_resumo(resumo, tamanhos):
    """Calcula speedup, eficiência e Karp--Flatt de cada configuração."""
    base = {(t): resumo[("sequencial", t, 1)]["mediana"] for t in tamanhos
            if ("sequencial", t, 1) in resumo}
    professor = {(t): resumo[("sequencial_original", t, 1)]["mediana"] for t in tamanhos
                 if ("sequencial_original", t, 1) in resumo}
    linhas = []
    for (versao, tamanho, workers), dados in sorted(
            resumo.items(), key=lambda kv: (kv[0][1], ORDEM_VERSOES.index(kv[0][0])
                                            if kv[0][0] in ORDEM_VERSOES else 99, kv[0][2])):
        t1 = base.get(tamanho)
        s = speedup(t1, dados["mediana"]) if t1 else None
        f = karp_flatt(s, workers) if s and workers > 1 else None
        linhas.append({
            "versao": versao,
            "linhas": tamanho,
            "workers": workers,
            "repeticoes": dados["repeticao"],
            "mediana_s": round(dados["mediana"], 6),
            "desvio_s": round(dados["desvio"], 6),
            "minimo_s": round(dados["minimo"], 6),
            "maximo_s": round(dados["maximo"], 6),
            "mediana_total_s": (round(dados["mediana_total"], 6)
                                if dados["mediana_total"] is not None else None),
            "speedup_vs_refatorada": round(s, 4) if s else None,
            "speedup_vs_professor": (round(speedup(professor[tamanho], dados["mediana"]), 4)
                                     if professor.get(tamanho) else None),
            "eficiencia": round(eficiencia(s, workers), 4) if s else None,
            "karp_flatt": round(f, 4) if f is not None else None,
            # Amdahl usa a fração serial medida desta própria configuração; o
            # limite com p->infinito é 1/f (coluna separada para o relatório).
            # Karp--Flatt fica negativo quando o speedup é superlinear (S_p > p),
            # o que acontece por efeito de cache quando cada worker passa a caber
            # no cache. Amdahl e Gustafson não têm sentido com f < 0: nesses
            # casos as colunas ficam vazias em vez de mostrar um número absurdo.
            "amdahl_previsto": (round(amdahl(f, workers), 4) if f is not None and f > 0
                                else None),
            "amdahl_limite": round(1.0 / f, 2) if f is not None and f > 0 else None,
            "gustafson_escalado": (round(gustafson(f, workers), 4)
                                   if f is not None and f > 0 else None),
            "superlinear": bool(s is not None and s > workers),
            "geracoes": dados["linha"]["geracoes_executadas"],
            "espalhadores_finais": dados["linha"]["espalhadores"],
        })
    return linhas


# ---------------------------------------------------------------------------
# Saída: CSV + tabelas Markdown
# ---------------------------------------------------------------------------

def gravar_resumo(linhas, caminho):
    """Grava o resumo agregado em CSV."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def _md(valor, casas=4):
    """Formata um número para Markdown (— quando não se aplica)."""
    if valor is None:
        return "—"
    if isinstance(valor, float):
        return f"{valor:.{casas}f}"
    return str(valor)


def _tabela(cabecalho, linhas):
    """Monta uma tabela Markdown a partir de listas de células."""
    saida = ["| " + " | ".join(cabecalho) + " |",
             "|" + "|".join("---" for _ in cabecalho) + "|"]
    for linha in linhas:
        saida.append("| " + " | ".join(str(c) for c in linha) + " |")
    return "\n".join(saida)


def gerar_tabelas(resumo_linhas, equivalencia, texto_equivalencia):
    """Monta o Markdown com as tabelas do relatório."""
    tamanhos = sorted({l["linhas"] for l in resumo_linhas})
    partes = ["# Tabelas dos experimentos", "",
              "Gerado por `python -m experimentos.analisar`. "
              "Tempos em segundos, mediana das repetições.", ""]

    partes += ["## Equivalência das versões", "", texto_equivalencia, ""]

    # Tabela 1: tempo por versão e trabalhadores (uma tabela por tamanho).
    for tamanho in tamanhos:
        partes += [f"## Tempo por configuração — grade {tamanho} x {tamanho}", ""]
        linhas = []
        for l in resumo_linhas:
            if l["linhas"] != tamanho:
                continue
            linhas.append([ROTULOS.get(l["versao"], l["versao"]), l["workers"],
                           _md(l["mediana_s"]), _md(l["desvio_s"]),
                           _md(l["mediana_total_s"]),
                           _md(l["speedup_vs_professor"], 2),
                           _md(l["speedup_vs_refatorada"], 2),
                           _md(l["eficiencia"], 3), _md(l["karp_flatt"], 3),
                           _md(l["amdahl_limite"], 2), _md(l["gustafson_escalado"], 2)])
        partes += [_tabela(
            ["Versão", "*workers*", "Mediana (s)", "Desvio (s)", "Total (s)",
             "Speedup vs prof.", "Speedup vs ref.", "Eficiência", "Karp–Flatt",
             "Amdahl 1/f", "Gustafson S'"],
            linhas), "",
            "— = não se aplica. Karp–Flatt negativo com `1/f` vazio significa "
            "**speedup superlinear** ($S_p > p$), típico de efeito de cache quando "
            "a faixa de cada worker passa a caber no cache; nesse caso as leis de "
            "Amdahl e Gustafson não têm sentido físico e são omitidas.", ""]

    # Tabela 2: melhorias (comparação das versões seriais e de 1 trabalhador).
    partes += ["## Impacto das melhorias (1 trabalhador)", ""]
    linhas = []
    for tamanho in tamanhos:
        for versao in ORDEM_VERSOES:
            chave = (versao, tamanho, 1)
            alvo = next((l for l in resumo_linhas
                         if l["versao"] == versao and l["linhas"] == tamanho
                         and l["workers"] == 1), None)
            if alvo is None:
                continue
            base = next((l for l in resumo_linhas
                         if l["versao"] == "sequencial_original" and l["linhas"] == tamanho), None)
            ganho = (base["mediana_s"] / alvo["mediana_s"]) if base else None
            linhas.append([tamanho, ROTULOS.get(versao, versao), _md(alvo["mediana_s"]),
                           _md(ganho, 2)])
    partes += [_tabela(["Grade", "Versão", "Mediana (s)",
                        "Ganho vs professor (×)"], linhas), ""]
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def gerar_graficos(resumo, resumo_linhas, pasta):
    """
    Gera os gráficos do relatório com matplotlib.

    matplotlib é opcional: se não estiver instalado, avisa e segue (as tabelas
    não dependem dele). Só é usado aqui, fora da simulação, como o enunciado
    exige.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # sem janela: só grava arquivo
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado — gráficos não gerados "
              "(pip install matplotlib). As tabelas foram geradas normalmente.")
        return []

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    gerados = []
    tamanhos = sorted({l["linhas"] for l in resumo_linhas})
    # Grades em que só existe versão de 1 trabalhador (o caso da bateria do
    # professor, grade 500²) não têm curva de speedup: um painel só com a linha
    # ideal ficaria vazio e confundiria a leitura.
    tamanhos_escala = [t for t in tamanhos
                       if any(l["workers"] > 1 for l in resumo_linhas if l["linhas"] == t)]
    if not tamanhos_escala:  # nada paralelo medido: usa todas as grades
        tamanhos_escala = tamanhos

    def _serie(versao, tamanho):
        pontos = [(l["workers"], l["mediana_s"]) for l in resumo_linhas
                  if l["versao"] == versao and l["linhas"] == tamanho]
        return [p[0] for p in sorted(pontos)], [p[1] for p in sorted(pontos)]

    # 1. Speedup por trabalhador (uma curva por versão, um painel por tamanho).
    figura, eixos = plt.subplots(1, len(tamanhos_escala),
                                 figsize=(5.2 * len(tamanhos_escala), 4.2), squeeze=False)
    for coluna, tamanho in enumerate(tamanhos_escala):
        eixo = eixos[0][coluna]
        for versao in ORDEM_VERSOES:
            xs, ys = _serie(versao, tamanho)
            pontos = [(x, y) for x, y in zip(xs, ys) if x > 1]
            if not pontos:
                continue
            base = next((l["mediana_s"] for l in resumo_linhas
                         if l["versao"] == "sequencial" and l["linhas"] == tamanho), None)
            if base is None:
                continue
            eixo.plot([p[0] for p in pontos], [base / p[1] for p in pontos],
                      marker=MARCADORES.get(versao, "o"), color=CORES.get(versao),
                      label=ROTULOS.get(versao, versao), linewidth=1.8)
        limite = max([l["workers"] for l in resumo_linhas
                      if l["linhas"] == tamanho] or [1])
        eixo.plot([1, limite], [1, limite], linestyle="--", color="#adb5bd",
                  linewidth=1, label="Ideal (linear)")
        eixo.set_title(f"Grade {tamanho} × {tamanho}")
        eixo.set_xlabel("Trabalhadores (p)")
        eixo.set_ylabel("Speedup  $S_p = T_1 / T_p$")
        eixo.grid(alpha=0.3)
        eixo.legend(fontsize=7)
    figura.suptitle("Speedup em relação à versão sequencial refatorada")
    figura.tight_layout()
    caminho = pasta / "speedup.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    gerados.append(caminho)

    # 2. Eficiência.
    figura, eixo = plt.subplots(figsize=(6.4, 4.2))
    for tamanho in tamanhos_escala:
        for versao in ("paralela_processos", "distribuida_local", "distribuida_bits"):
            pontos = [(l["workers"], l["eficiencia"]) for l in resumo_linhas
                      if l["versao"] == versao and l["linhas"] == tamanho
                      and l["workers"] > 1 and l["eficiencia"] is not None]
            if not pontos:
                continue
            eixo.plot([p[0] for p in pontos], [p[1] for p in pontos],
                      marker=MARCADORES.get(versao, "o"), color=CORES.get(versao),
                      linestyle="-" if tamanho == tamanhos_escala[-1] else "--",
                      label=f"{ROTULOS.get(versao, versao)} — {tamanho}²",
                      linewidth=1.6)
    eixo.set_xlabel("Trabalhadores (p)")
    eixo.set_ylabel("Eficiência  $E_p = S_p / p$")
    eixo.set_ylim(0, 1.15)
    eixo.grid(alpha=0.3)
    eixo.legend(fontsize=7)
    eixo.set_title("Eficiência das versões paralela e distribuída")
    figura.tight_layout()
    caminho = pasta / "eficiencia.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    gerados.append(caminho)

    # 3. Efeito do GIL: threads contra processos.
    figura, eixo = plt.subplots(figsize=(6.4, 4.2))
    for tamanho in tamanhos_escala:
        for versao in ("paralela_threads", "paralela_processos"):
            xs, ys = _serie(versao, tamanho)
            pontos = [(x, y) for x, y in zip(xs, ys) if x > 1]
            if not pontos:
                continue
            eixo.plot([p[0] for p in pontos], [p[1] for p in pontos],
                      marker=MARCADORES.get(versao, "o"), color=CORES.get(versao),
                      linestyle="-" if tamanho == tamanhos_escala[-1] else "--",
                      label=f"{ROTULOS.get(versao, versao)} — {tamanho}²", linewidth=1.6)
    eixo.set_xlabel("Trabalhadores (p)")
    eixo.set_ylabel("Tempo do laço (s)")
    eixo.set_yscale("log")
    eixo.grid(alpha=0.3, which="both")
    eixo.legend(fontsize=7)
    eixo.set_title("Threads × processos: o efeito do GIL (escala log)")
    figura.tight_layout()
    caminho = pasta / "gil.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    gerados.append(caminho)

    # 4. Impacto das melhorias.
    figura, eixo = plt.subplots(figsize=(6.8, 4.2))
    largura = 0.8 / max(1, len(ORDEM_VERSOES))
    for indice, versao in enumerate(ORDEM_VERSOES):
        valores = []
        for tamanho in tamanhos:
            alvo = next((l["mediana_s"] for l in resumo_linhas
                         if l["versao"] == versao and l["linhas"] == tamanho
                         and l["workers"] == 1), None)
            valores.append(alvo)
        if all(v is None for v in valores):
            continue
        posicoes = [i + indice * largura for i in range(len(tamanhos))]
        eixo.bar(posicoes, [v if v is not None else 0 for v in valores], largura,
                 label=ROTULOS.get(versao, versao), color=CORES.get(versao),
                 edgecolor="white", linewidth=0.4)
    eixo.set_xticks([i + 0.4 for i in range(len(tamanhos))])
    eixo.set_xticklabels([f"{t} × {t}" for t in tamanhos])
    eixo.set_ylabel("Mediana do laço (s)")
    eixo.set_title("Tempo com 1 trabalhador: impacto das melhorias")
    eixo.grid(alpha=0.3, axis="y")
    eixo.legend(fontsize=7)
    figura.tight_layout()
    caminho = pasta / "melhorias.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    gerados.append(caminho)

    return gerados


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    """Lê os CSVs, confere a equivalência e gera tabelas e gráficos."""
    parser = argparse.ArgumentParser(description="Analisa as medições de desempenho")
    parser.add_argument("--csv", nargs="+", default=None,
                        help="um ou mais CSVs de medição (as baterias são somadas); "
                             "sem esta opção, usa todos os medicoes_*.csv da pasta")
    parser.add_argument("--saida", default=str(PASTA))
    parser.add_argument("--sem-graficos", action="store_true")
    args = parser.parse_args(argv)

    _console_seguro()
    if args.csv:
        caminhos = [Path(c) for c in args.csv]
    else:
        # Sem argumento: todas as baterias gravadas. É o caso comum de quem só
        # rodou os `medir.py` e quer as tabelas finais.
        caminhos = sorted(PASTA.glob("medicoes_*.csv"))
        if not caminhos:
            print(f"Nenhum medicoes_*.csv em {PASTA}\n"
                  "Rode antes: python -m experimentos.medir")
            return 1
    faltando = [c for c in caminhos if not c.exists()]
    if faltando:
        print("CSV não encontrado: " + ", ".join(str(c) for c in faltando)
              + "\nRode antes: python -m experimentos.medir")
        return 1
    # Várias baterias (por exemplo, uma só para o GIL e outra para a
    # escalabilidade) são somadas aqui, em vez de obrigar a uma execução única.
    linhas = []
    for caminho in caminhos:
        carregadas = carregar(caminho)
        print(f"  {caminho.name}: {len(carregadas)} medições")
        linhas.extend(carregadas)
    resumo = agrupar(linhas)
    equivalencia, divergencias, tamanhos = verificar_equivalencia(linhas)
    resumo_linhas = montar_resumo(resumo, tamanhos)
    if not resumo_linhas:
        print("Nenhuma configuração para analisar.")
        return 1

    pasta = Path(args.saida)
    gravar_resumo(resumo_linhas, pasta / "resumo.csv")

    if equivalencia:
        texto = ("✅ Todas as versões produziram **a mesma grade final** em todas as "
                 f"execuções (grades {', '.join(f'{t}×{t}' for t in tamanhos)}). "
                 "O experimento também vale como teste de equivalência em escala.")
        console = ("[OK] Todas as versoes produziram a mesma grade final em todas as "
                   f"execucoes (grades {', '.join(f'{t}x{t}' for t in tamanhos)}).")
    else:
        texto = ("❌ **Divergência encontrada** — as versões não produziram a mesma grade:\n\n"
                 + "\n".join(f"- {v} {t}² workers={w}: {h} ≠ {e}"
                             for v, t, w, h, e in divergencias[:10]))
        console = ("[FALHA] Divergencia encontrada — as versoes nao produziram a mesma grade:\n"
                   + "\n".join(f"  - {v} {t}x{t} workers={w}: {h} != {e}"
                               for v, t, w, h, e in divergencias[:10]))
    (pasta / "tabelas.md").write_text(gerar_tabelas(resumo_linhas, equivalencia, texto),
                                     encoding="utf-8")

    print(console)
    print(f"\nTabelas: {pasta / 'tabelas.md'}")
    print(f"Resumo:  {pasta / 'resumo.csv'}")

    if not args.sem_graficos:
        gerados = gerar_graficos(resumo, resumo_linhas, pasta / "graficos")
        for g in gerados:
            print(f"Gráfico: {g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
