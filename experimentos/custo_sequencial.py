"""
Custo da versão sequencial fornecida (código do professor).

Dá os números da análise de custo da versão sequencial no relatório. São três
medições independentes:

1. Perfil de uma geração (depende da máquina)
   Com as funções do professor, sem alterá-las, mede por geração o tempo de
   `proxima_geracao`, o tempo de um `deepcopy` da mesma grade e o tempo de
   `contar_estados`. Como o `deepcopy` acontece DENTRO de `proxima_geracao` e o
   arquivo original não pode ser alterado, ele é medido à parte, numa cópia da
   mesma grade; o tempo da varredura (o laço sobre as células) é estimado por
   diferença: varredura = proxima_geracao - deepcopy.
   Também registra quantos ignorantes havia na grade de entrada, porque só os
   ignorantes contam vizinhos: o custo de uma geração depende do estado.

2. Limiar x percentual inicial (não depende da máquina)
   Para cada combinação, roda até não haver espalhadores e anota quantas
   gerações a simulação dura, o pico de espalhadores e o alcance final. Usa a
   sequencial refatorada (comum/modelo.py), que produz as mesmas grades que o
   código do professor (testes de equivalência), porque o original levaria
   horas nas combinações mais longas.

3. Memória da grade (depende só da versão do Python)
   Com `tracemalloc`, mede quanto ocupa a grade como lista de listas (formato
   do professor), uma cópia com `deepcopy`, o pico de memória de uma chamada de
   `proxima_geracao` e a mesma grade como vetor de bytes (formato refatorado).

Saídas (em experimentos/resultados/, ou em --saida):
- custo_perfil.csv     uma linha por (repetição, geração)
- custo_limiar.csv     uma linha por (limiar, percentual)
- custo_memoria.csv    uma linha por estrutura medida
- custo_ambiente.csv   máquina em que o perfil foi medido
- custo_sequencial.md  tabelas prontas para o relatório

Uso (da raiz do repositório):
    python -m experimentos.custo_sequencial --cpu "nome do processador"
    python -m experimentos.custo_sequencial --rapido     # fumaça, em segundos

Com --rapido as grades são pequenas e, se --saida não for dada, os arquivos vão
para uma pasta temporária (para não sobrescrever os resultados de verdade).
"""

import argparse
import csv
import statistics
import sys
import tempfile
import time
import tracemalloc
from copy import deepcopy
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from comum import modelo  # noqa: E402
from comum.estatisticas import Estatisticas  # noqa: E402
from comum.parametros import ParametrosSimulacao  # noqa: E402
from experimentos.medir import descrever_ambiente, gravar_ambiente  # noqa: E402
from sequencial.fakenews_sequencial import executar_simulacao  # noqa: E402
from sequencial.fakenews_sequencial_original import (  # noqa: E402
    ESPALHADOR,
    IGNORANTE,
    contar_estados,
    criar_grade,
    proxima_geracao,
)

PASTA = RAIZ / "experimentos" / "resultados"

LIMIARES = (1, 2, 3)
PERCENTUAIS = (0.01, 0.02, 0.05, 0.10)

AMBIENTE_PADRAO = ("notebook na tomada, demais programas fechados; "
                   "execução serial (um único processo)")


def _console_seguro():
    """Evita que um acento fora da tabela do terminal derrube a medição."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")


def _gravar_csv(caminho, linhas):
    """Grava uma lista de dicionários em CSV (UTF-8, sem linha em branco no Windows)."""
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)


# ---------------------------------------------------------------------------
# 1. Perfil de uma geração do código do professor
# ---------------------------------------------------------------------------

def medir_perfil_uma_vez(lado, geracoes, percentual, limiar, semente, repeticao):
    """
    Roda o laço do professor uma vez, medindo cada etapa de cada geração.

    Devolve uma linha por geração. Nada é impresso dentro do laço, como em
    experimentos/medir.py, para o tempo não incluir saída no terminal.
    """
    grade = criar_grade(lado, lado, percentual, semente)
    ignorantes = contar_estados(grade)[IGNORANTE]  # fora da medição
    linhas = []
    for geracao in range(1, geracoes + 1):
        # deepcopy medido à parte, sobre a mesma grade que proxima_geracao copia.
        inicio = time.perf_counter()
        copia = deepcopy(grade)
        tempo_copia = time.perf_counter() - inicio
        del copia

        inicio = time.perf_counter()
        nova = proxima_geracao(grade, limiar)
        tempo_proxima = time.perf_counter() - inicio

        inicio = time.perf_counter()
        contagem = contar_estados(nova)
        tempo_contagem = time.perf_counter() - inicio

        linhas.append({
            "linhas": lado,
            "colunas": lado,
            "percentual": percentual,
            "limiar": limiar,
            "repeticao": repeticao,
            "geracao": geracao,
            "ignorantes_entrada": ignorantes,
            "tempo_proxima_geracao_s": tempo_proxima,
            "tempo_deepcopy_s": tempo_copia,
            "tempo_varredura_s": tempo_proxima - tempo_copia,
            "tempo_contar_estados_s": tempo_contagem,
        })
        grade = nova
        ignorantes = contagem[IGNORANTE]
        if contagem[ESPALHADOR] == 0:
            break
    return linhas


def medir_perfil(lado, geracoes, percentual, limiar, semente, repeticoes, aquecimento):
    """Aquecimento descartado + repetições; devolve todas as linhas medidas."""
    for _ in range(aquecimento):
        medir_perfil_uma_vez(lado, geracoes, percentual, limiar, semente, 0)
    todas = []
    for repeticao in range(1, repeticoes + 1):
        comeco = time.perf_counter()
        todas += medir_perfil_uma_vez(lado, geracoes, percentual, limiar, semente, repeticao)
        print(f"    repetição {repeticao}: {time.perf_counter() - comeco:.1f} s")
    return todas


def resumir_perfil(linhas):
    """
    Soma cada etapa por repetição e tira a mediana entre as repetições.

    O total de uma geração do professor é proxima_geracao + contar_estados
    (é o que o laço de executar_simulacao faz, sem contar a impressão).
    """
    por_repeticao = {}
    for linha in linhas:
        soma = por_repeticao.setdefault(linha["repeticao"], {
            "deepcopy": 0.0, "varredura": 0.0, "contar_estados": 0.0, "geracoes": 0})
        soma["deepcopy"] += float(linha["tempo_deepcopy_s"])
        soma["varredura"] += float(linha["tempo_varredura_s"])
        soma["contar_estados"] += float(linha["tempo_contar_estados_s"])
        soma["geracoes"] += 1
    etapas = ("deepcopy", "varredura", "contar_estados")
    mediana = {etapa: statistics.median(s[etapa] for s in por_repeticao.values())
               for etapa in etapas}
    geracoes = statistics.median(s["geracoes"] for s in por_repeticao.values())
    total = sum(mediana.values())
    return [{"etapa": etapa,
             "tempo_total_s": round(mediana[etapa], 4),
             "tempo_por_geracao_s": round(mediana[etapa] / geracoes, 5),
             "percentual": round(100 * mediana[etapa] / total, 1)}
            for etapa in etapas] + [{
                "etapa": "total",
                "tempo_total_s": round(total, 4),
                "tempo_por_geracao_s": round(total / geracoes, 5),
                "percentual": 100.0}]


def ajustar_custo_por_estado(linhas):
    """
    Estima quanto custa visitar uma célula ignorante e uma de outro estado.

    Modelo: varredura = c_I * N_I + c_O * (L*C - N_I) = c_O * L*C + (c_I - c_O) * N_I,
    em que N_I é o número de ignorantes na grade de entrada. Como N_I cai ao
    longo das gerações, a reta "tempo da varredura x N_I" (mínimos quadrados,
    mediana das repetições em cada geração) dá os dois custos:
    intercepto = c_O * L*C e inclinação = c_I - c_O.
    """
    celulas = int(linhas[0]["linhas"]) * int(linhas[0]["colunas"])
    tempos, ignorantes = {}, {}
    for linha in linhas:
        geracao = int(linha["geracao"])
        tempos.setdefault(geracao, []).append(float(linha["tempo_varredura_s"]))
        ignorantes[geracao] = int(linha["ignorantes_entrada"])
    xs = [ignorantes[g] for g in sorted(tempos)]
    ys = [statistics.median(tempos[g]) for g in sorted(tempos)]
    inclinacao, intercepto = statistics.linear_regression(xs, ys)
    custo_outros = intercepto / celulas
    custo_ignorante = custo_outros + inclinacao
    return {
        "pontos": len(xs),
        "ignorantes_min": min(xs),
        "ignorantes_max": max(xs),
        "correlacao": round(statistics.correlation(xs, ys), 4),
        "custo_ignorante_us": round(custo_ignorante * 1e6, 3),
        "custo_outros_us": round(custo_outros * 1e6, 3),
        "razao": round(custo_ignorante / custo_outros, 1),
    }


# ---------------------------------------------------------------------------
# 2. Limiar x percentual inicial
# ---------------------------------------------------------------------------

def medir_limiares(lado, teto_geracoes, semente):
    """Roda cada (limiar, percentual) até parar e resume a dinâmica."""
    resultados = []
    total = lado * lado
    for limiar in LIMIARES:
        for percentual in PERCENTUAIS:
            parametros = ParametrosSimulacao(
                linhas=lado, colunas=lado, geracoes=teto_geracoes,
                percentual_espalhadores=percentual, limiar=limiar, semente=semente)
            estatisticas = Estatisticas("limiar", parametros, 1)
            resultado = executar_simulacao(parametros, mostrar=False,
                                           estatisticas=estatisticas)
            resumo = estatisticas.resumo()
            contagem = resultado["contagem"]
            linha = {
                "linhas": lado,
                "colunas": lado,
                "limiar": limiar,
                "percentual": percentual,
                # Estatisticas só registra da geração 1 em diante; a inicial é contada aqui.
                "espalhadores_iniciais": contar_estados(
                    criar_grade(lado, lado, percentual, semente))[ESPALHADOR],
                "geracoes_ate_parar": resultado["geracoes_executadas"],
                # Se chegou ao teto ainda com espalhadores, a duração é "pelo menos".
                "parou_sozinha": contagem[modelo.ESPALHADOR] == 0,
                "pico_espalhadores": resumo["pico_espalhadores"],
                "geracao_do_pico": resumo["geracao_do_pico"],
                # Alcance: fração que deixou de ser ignorante (mesma definição de modelo.py).
                "alcance_final_pct": round(100 * (1 - contagem[modelo.IGNORANTE] / total), 2),
            }
            resultados.append(linha)
            print(f"    limiar {limiar}, {percentual * 100:.0f}%: "
                  f"{linha['geracoes_ate_parar']} gerações, alcance "
                  f"{linha['alcance_final_pct']:.2f}%")
    return resultados


# ---------------------------------------------------------------------------
# 3. Memória da grade
# ---------------------------------------------------------------------------

def _memoria_de(funcao):
    """
    Executa `funcao()` com tracemalloc ligado.

    Devolve (resultado, bytes que continuam alocados depois, pico durante a
    chamada), os dois medidos em relação ao que já estava alocado antes.
    """
    tracemalloc.start()
    antes, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    resultado = funcao()
    depois, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, depois - antes, pico - antes


def medir_memoria(lado, percentual, limiar, semente):
    """Bytes por célula de cada forma de guardar a grade."""
    celulas = lado * lado
    grade, bytes_lista, _ = _memoria_de(lambda: criar_grade(lado, lado, percentual, semente))
    _, bytes_copia, _ = _memoria_de(lambda: deepcopy(grade))
    # Pico de uma geração: a cópia nova coexiste com a grade atual.
    _, bytes_nova, pico_geracao = _memoria_de(lambda: proxima_geracao(grade, limiar))
    _, bytes_plana, _ = _memoria_de(lambda: modelo.grade_para_plana(grade))
    medidas = [
        ("lista de listas (criar_grade)", bytes_lista),
        ("cópia com deepcopy", bytes_copia),
        ("grade nova devolvida por proxima_geracao", bytes_nova),
        ("pico durante proxima_geracao", pico_geracao),
        ("vetor de bytes com moldura (refatorada)", bytes_plana),
    ]
    return [{"linhas": lado, "colunas": lado, "estrutura": nome, "bytes": valor,
             "bytes_por_celula": round(valor / celulas, 2),
             "mib": round(valor / 1024 ** 2, 2)}
            for nome, valor in medidas]


# ---------------------------------------------------------------------------
# Resumo em Markdown (lido dos CSVs, para poder refazer só uma parte)
# ---------------------------------------------------------------------------

def _ler_csv(caminho):
    """Lê um CSV como lista de dicionários de texto (vazia se não existir)."""
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def gerar_markdown(pasta):
    """
    Tabelas prontas para o relatório, montadas a partir dos CSVs da pasta.

    Cada tabela diz as condições em que foi medida (lidas dos próprios CSVs),
    então rodar de novo só uma das partes não deixa o resumo inconsistente.
    """
    ambiente = {linha["item"]: linha["valor"]
                for linha in _ler_csv(pasta / "custo_ambiente.csv")}
    perfil_bruto = _ler_csv(pasta / "custo_perfil.csv")
    limiares = _ler_csv(pasta / "custo_limiar.csv")
    memoria = _ler_csv(pasta / "custo_memoria.csv")
    partes = ["# Custo da versão sequencial fornecida", "",
              "Gerado por `python -m experimentos.custo_sequencial`.", ""]

    if perfil_bruto:
        base = perfil_bruto[0]
        repeticoes = len({linha["repeticao"] for linha in perfil_bruto})
        geracoes = max(int(linha["geracao"]) for linha in perfil_bruto)
        partes += [
            f"## Perfil de uma geração (grade {base['linhas']} × {base['colunas']}, "
            f"{float(base['percentual']) * 100:.0f}% de espalhadores, limiar {base['limiar']}, "
            f"{geracoes} gerações)",
            "",
            f"Mediana de {repeticoes} repetições. Máquina: {ambiente.get('processador', '?')}, "
            f"{ambiente.get('sistema', '?')}, Python {ambiente.get('python', '?')}.",
            "",
            "| Etapa | Tempo total (s) | Por geração (s) | % |",
            "|---|---|---|---|",
        ]
        for linha in resumir_perfil(perfil_bruto):
            partes.append(f"| {linha['etapa']} | {linha['tempo_total_s']:.4f} | "
                          f"{linha['tempo_por_geracao_s']:.5f} | {linha['percentual']:.1f} |")
        ajuste = ajustar_custo_por_estado(perfil_bruto)
        partes += [
            "",
            "O `deepcopy` foi medido à parte, numa cópia da mesma grade; a varredura é "
            "`proxima_geracao` menos esse tempo (estimativa).",
            "",
            "### Custo por célula conforme o estado",
            "",
            "Reta de mínimos quadrados do tempo da varredura (mediana por geração) contra o "
            f"número de ignorantes na grade de entrada ({ajuste['pontos']} gerações, de "
            f"{ajuste['ignorantes_min']:,} a {ajuste['ignorantes_max']:,} ignorantes):",
            "",
            "| Custo por célula ignorante (µs) | Custo por célula de outro estado (µs) | "
            "Razão | Correlação |",
            "|---|---|---|---|",
            f"| {ajuste['custo_ignorante_us']:.3f} | {ajuste['custo_outros_us']:.3f} | "
            f"{ajuste['razao']:.1f} | {ajuste['correlacao']:.4f} |",
            "",
        ]

    if limiares:
        base = limiares[0]
        partes += [
            f"## Limiar × percentual inicial (grade {base['linhas']} × {base['colunas']}, "
            "até não haver espalhadores)",
            "",
            "| Limiar | % inicial | Espalhadores iniciais | Gerações até parar | "
            "Pico de espalhadores | Alcance final |",
            "|---|---|---|---|---|---|",
        ]
        for linha in limiares:
            geracoes = linha["geracoes_ate_parar"]
            if linha["parou_sozinha"] != "True":
                geracoes = f"≥ {geracoes} (teto)"
            partes.append(f"| {linha['limiar']} | {float(linha['percentual']) * 100:.0f}% | "
                          f"{int(linha['espalhadores_iniciais']):,} | {geracoes} | "
                          f"{int(linha['pico_espalhadores']):,} | "
                          f"{float(linha['alcance_final_pct']):.2f}% |")
        partes.append("")

    if memoria:
        base = memoria[0]
        partes += [
            f"## Memória da grade ({base['linhas']} × {base['colunas']}, "
            f"Python {ambiente.get('python', '?')})",
            "",
            "| Estrutura | MiB | Bytes por célula |",
            "|---|---|---|",
        ]
        for linha in memoria:
            partes.append(f"| {linha['estrutura']} | {float(linha['mib']):.2f} | "
                          f"{float(linha['bytes_por_celula']):.2f} |")
        partes += ["", "Os valores são relativos ao que já estava alocado antes de cada "
                   "medida; o pico de `proxima_geracao` não inclui a grade de entrada, que "
                   "continua viva durante a chamada."]
    return "\n".join(partes) + "\n"


def main(argv=None):
    """Roda as medições pedidas, grava os CSVs e refaz o Markdown."""
    _console_seguro()
    parser = argparse.ArgumentParser(
        description="Custo de tempo e memória da versão sequencial fornecida")
    parser.add_argument("--partes", nargs="+", choices=("perfil", "limiar", "memoria"),
                        default=["perfil", "limiar", "memoria"],
                        help="quais medições rodar (o resumo usa os CSVs que existirem)")
    parser.add_argument("--lado", type=int, default=1000,
                        help="lado da grade do perfil e da memória")
    parser.add_argument("--geracoes", type=int, default=20)
    parser.add_argument("--percentual", type=float, default=0.05)
    parser.add_argument("--limiar", type=int, default=2)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--repeticoes", type=int, default=5)
    parser.add_argument("--aquecimento", type=int, default=1)
    parser.add_argument("--lado-limiar", type=int, default=1000,
                        help="lado da grade da tabela limiar x percentual")
    parser.add_argument("--teto", type=int, default=5000,
                        help="máximo de gerações na tabela limiar x percentual")
    parser.add_argument("--saida", help="pasta dos resultados (padrão: experimentos/resultados)")
    parser.add_argument("--cpu", help="nome do processador para o relatório")
    parser.add_argument("--nucleos-fisicos", type=int)
    parser.add_argument("--ambiente", default=AMBIENTE_PADRAO,
                        help="condição da medição (na tomada? outros programas abertos?)")
    parser.add_argument("--rapido", action="store_true",
                        help="grades pequenas, 2 repetições: só confere se tudo roda")
    args = parser.parse_args(argv)

    if args.rapido:
        args.lado, args.lado_limiar, args.geracoes = 100, 100, 3
        args.repeticoes, args.aquecimento, args.teto = 2, 0, 500
        if args.saida is None:
            args.saida = tempfile.mkdtemp(prefix="custo_sequencial_")
    pasta = Path(args.saida) if args.saida else PASTA
    pasta.mkdir(parents=True, exist_ok=True)

    if "perfil" in args.partes:
        # A máquina só importa para o perfil (as outras partes não medem tempo).
        ambiente = descrever_ambiente(args.cpu, args.nucleos_fisicos, args.ambiente)
        gravar_ambiente(ambiente, pasta / "custo_ambiente.csv")
        print(f"Perfil por etapa ({args.lado} × {args.lado}, {args.geracoes} gerações)",
              flush=True)
        linhas_perfil = medir_perfil(args.lado, args.geracoes, args.percentual, args.limiar,
                                     args.semente, args.repeticoes, args.aquecimento)
        _gravar_csv(pasta / "custo_perfil.csv", linhas_perfil)

    if "limiar" in args.partes:
        print(f"Limiar × percentual ({args.lado_limiar} × {args.lado_limiar})", flush=True)
        _gravar_csv(pasta / "custo_limiar.csv",
                    medir_limiares(args.lado_limiar, args.teto, args.semente))

    if "memoria" in args.partes:
        print(f"Memória ({args.lado} × {args.lado})", flush=True)
        _gravar_csv(pasta / "custo_memoria.csv",
                    medir_memoria(args.lado, args.percentual, args.limiar, args.semente))

    resumo = gerar_markdown(pasta)
    (pasta / "custo_sequencial.md").write_text(resumo, encoding="utf-8")
    print(resumo)
    print(f"Resultados em {pasta}")


if __name__ == "__main__":
    main()
