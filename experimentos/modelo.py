"""
Efeito das melhorias do MODELO (não do desempenho): resistência individual e bots.

Item 4 da checklist de experimentos do grupo: "espalhadores por geração com e sem
resistência e bots".

Como a comparação é justa
-------------------------
Os quatro cenários partem da MESMA grade inicial: `comum/modelo.py` sorteia a
grade com `semente`, os limiares individuais com `semente + 1` e os bots com
`semente + 2`, em geradores separados. Ligar uma melhoria não desloca a
sequência de sorteios das outras, então a diferença nas curvas vem da regra, não
do acaso.

Por que medir no sequencial
---------------------------
O modelo é o mesmo nas três versões (núcleo comum). Rodar no sequencial evita o
ruído de processos e rede e mantém a curva idêntica à das outras versões — o que
os testes de equivalência já garantem.

Saídas
------
- `resultados/modelo_geracoes.csv`: uma linha por (cenário, geração).
- `resultados/modelo_resumo.csv`: pico, geração do pico, alcance e duração.
- `resultados/modelo.md`: tabela pronta para o relatório.
- `resultados/graficos/modelo.png`: espalhadores por geração (matplotlib opcional).

Uso:
    python -m experimentos.modelo
    python -m experimentos.modelo --linhas 500 --geracoes 60 --limiar 2
"""

import argparse
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from comum import modelo  # noqa: E402
from comum.estatisticas import Estatisticas  # noqa: E402
from comum.parametros import ParametrosSimulacao  # noqa: E402
from sequencial.fakenews_sequencial import executar_simulacao  # noqa: E402

PASTA = RAIZ / "experimentos" / "resultados"

# Cada cenário é um conjunto de argumentos de ParametrosSimulacao. A ordem aqui é
# a ordem das curvas no gráfico e da tabela.
#
# Atenção ao desenho: a linha de base usa limiar fixo 2 para todos. Uma
# resistência sorteada entre 1 e 3 tem MÉDIA 2, mas metade da população passa a
# precisar de só 1 vizinho — isso facilita a propagação, não dificulta. Para
# medir "população mais difícil de convencer" é preciso uma faixa acima do
# limiar da base (3–5). Os dois cenários entram, porque a comparação honesta é
# essa: a heterogeneidade por si só já muda o resultado.
CENARIOS = {
    "sem melhorias (limiar 2 fixo)": {},
    "resistência 1–3 (média = base)": {"resistencia": (1, 3)},
    "resistência 3–5 (mais resistente)": {"resistencia": (3, 5)},
    "bots 2%": {"fracao_bots": 0.02},
    "bots 2% + resistência 3–5": {"fracao_bots": 0.02, "resistencia": (3, 5)},
}

CORES = ["#2b2d42", "#0a9396", "#8d99ae", "#e07a5f", "#9b5de5"]


def _console_seguro():
    """Evita que um acento fora da tabela do terminal derrube a medição."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")


def medir_cenario(nome, extra, base):
    """Roda um cenário e devolve (linhas por geração, resumo)."""
    parametros = ParametrosSimulacao(
        linhas=base.linhas, colunas=base.colunas, geracoes=base.geracoes,
        percentual_espalhadores=base.percentual_espalhadores, limiar=base.limiar,
        semente=base.semente, **extra)
    estatisticas = Estatisticas(nome, parametros, 1)
    executar_simulacao(parametros, mostrar=False, estatisticas=estatisticas)
    resumo = estatisticas.resumo()
    total = parametros.linhas * parametros.colunas
    final = estatisticas.geracoes[-1]
    resumo.update({
        "cenario": nome,
        "geracoes": len(estatisticas.geracoes),
        "espalhadores_finais": final["espalhadores"],
        # Fração que passou pela notícia (deixou de ser ignorante).
        "alcance_final_pct": round(100 * (1 - final["ignorantes"] / total), 2),
    })
    return estatisticas.geracoes, resumo


def gerar_tabela(resumos, base):
    """Tabela Markdown com o efeito de cada melhoria."""
    referencia = resumos[0]["alcance_final_pct"] if resumos else None
    partes = [
        "# Efeito das melhorias do modelo",
        "",
        f"Mesma grade ({base.linhas} × {base.colunas}, semente {base.semente}, "
        f"{base.percentual_espalhadores * 100:.0f}% de espalhadores iniciais, "
        f"limiar {base.limiar}).",
        "",
        "| Cenário | Pico de espalhadores | Geração do pico | Alcance final | "
        "Alcance vs base | Espalhadores no fim | Gerações até parar |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in resumos:
        delta = (r["alcance_final_pct"] - referencia) if referencia is not None else None
        texto_delta = "—" if delta is None else f"{delta:+.2f} p.p."
        partes.append(
            f"| {r['cenario']} | {r['pico_espalhadores']:,} | {r['geracao_do_pico']} | "
            f"{r['alcance_final_pct']:.2f}% | {texto_delta} | "
            f"{r['espalhadores_finais']:,} | {r['geracoes']} |")
    partes += [
        "",
        "**Como ler.** *Alcance* é a fração da população que deixou de ser ignorante. "
        "Compare sempre com a primeira linha:",
        "",
        "- **resistência 1–3** tem média igual ao limiar da base, mas metade da população "
        "passa a precisar de apenas 1 vizinho; o alcance sobe por isso. A heterogeneidade, "
        "sozinha, facilita a propagação — não é \"mais resistência\".",
        "- **resistência 3–5** é o cenário de população mais difícil de convencer (todos "
        "acima do limiar da base) e serve para o efeito oposto.",
        "- **bots** nunca deixam de espalhar: a simulação só termina no limite de gerações "
        "e os espalhadores humanos zeram enquanto os bots permanecem.",
    ]
    return "\n".join(partes)


def gerar_grafico(curvas, resumos, pasta):
    """Espalhadores por geração, uma linha por cenário (matplotlib opcional)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado — gráfico não gerado. As tabelas saíram normalmente.")
        return None

    figura, (eixo1, eixo2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for indice, (nome, geracoes) in enumerate(curvas.items()):
        cor = CORES[indice % len(CORES)]
        xs = [g["geracao"] for g in geracoes]
        eixo1.plot(xs, [g["espalhadores"] for g in geracoes], color=cor, label=nome,
                   linewidth=1.8)
        eixo2.plot(xs, [g["inativos"] for g in geracoes], color=cor, label=nome,
                   linewidth=1.8)
    eixo1.set_title("Espalhadores por geração")
    eixo1.set_xlabel("Geração")
    eixo1.set_ylabel("Espalhadores")
    eixo2.set_title("Inativos (já deixaram de espalhar)")
    eixo2.set_xlabel("Geração")
    eixo2.set_ylabel("Inativos")
    for eixo in (eixo1, eixo2):
        eixo.grid(alpha=0.3)
        eixo.legend(fontsize=7)
    figura.suptitle("Efeito das melhorias do modelo: resistência individual e bots")
    figura.tight_layout()
    caminho = pasta / "graficos" / "modelo.png"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    return caminho


def main(argv=None):
    """Roda os cenários, grava CSVs, tabela e gráfico."""
    _console_seguro()
    parser = argparse.ArgumentParser(
        description="Mede o efeito das melhorias do modelo (resistência e bots)")
    parser.add_argument("--linhas", type=int, default=1000)
    parser.add_argument("--geracoes", type=int, default=60,
                        help="máximo de gerações (com bots a simulação só para aqui)")
    parser.add_argument("--limiar", type=int, default=2)
    parser.add_argument("--percentual", type=float, default=0.05)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", default=str(PASTA))
    parser.add_argument("--sem-graficos", action="store_true")
    args = parser.parse_args(argv)

    base = ParametrosSimulacao(linhas=args.linhas, colunas=args.linhas,
                               geracoes=args.geracoes, limiar=args.limiar,
                               percentual_espalhadores=args.percentual,
                               semente=args.semente)
    pasta = Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)

    curvas, resumos = {}, []
    for nome, extra in CENARIOS.items():
        print(f"  {nome} ... ", end="", flush=True)
        geracoes, resumo = medir_cenario(nome, extra, base)
        curvas[nome] = geracoes
        resumos.append(resumo)
        print(f"pico {resumo['pico_espalhadores']:,} na geração "
              f"{resumo['geracao_do_pico']}; alcance {resumo['alcance_final_pct']:.2f}%; "
              f"{resumo['geracoes']} gerações")

    with open(pasta / "modelo_geracoes.csv", "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["cenario", "geracao", "ignorantes", "espalhadores",
                           "inativos", "bots"])
        for nome, geracoes in curvas.items():
            for g in geracoes:
                escritor.writerow([nome, g["geracao"], g["ignorantes"],
                                   g["espalhadores"], g["inativos"], g["bots"]])

    campos = ["cenario", "geracoes", "pico_espalhadores", "geracao_do_pico",
              "alcance_final_pct", "espalhadores_finais"]
    with open(pasta / "modelo_resumo.csv", "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(resumos)

    tabela = gerar_tabela(resumos, base)
    (pasta / "modelo.md").write_text(tabela, encoding="utf-8")

    print()
    print(tabela)
    grafico = None
    if not args.sem_graficos:
        grafico = gerar_grafico(curvas, resumos, pasta)
        if grafico:
            print(f"\nGráfico: {grafico}")
    print(f"CSVs:   {pasta / 'modelo_geracoes.csv'} e {pasta / 'modelo_resumo.csv'}")
    print(f"Tabela: {pasta / 'modelo.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
