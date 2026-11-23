"""
Perfil de tempo por worker: quanto é cálculo, quanto é comunicação e quanto é
espera (sincronização), além do desbalanceamento de carga.

Esta é a métrica que o capítulo de experimentos pede como "tempo de comunicação
vs. cômputo". Ela não sai da medição de tempo total: só aparece porque cada
worker cronometra as próprias três fases (ver `comum/estatisticas.py` e o laço
em `paralelo/fakenews_paralelo.py` e `distribuido/worker.py`).

O que cada fase significa
-------------------------
- **cálculo**: dentro de `calcular_faixa` + `contar_faixa`.
- **comunicação**: troca das bordas (halo) e envio da contagem ao coordenador.
  Na versão paralela, com memória compartilhada, não há mensagens: 0.
- **espera**: parado na barreira (paralela) ou aguardando a `DECISAO`
  (distribuída). É o custo de sincronização visto de dentro do worker.

As três fases somam aproximadamente o tempo do laço de cada worker, então a
coluna `soma/tempo` serve de conferência: se ficar longe de 1,0, alguma coisa
do trabalho não está sendo contada.

Uso:
    python -m experimentos.perfis
    python -m experimentos.perfis --linhas 1000 --workers 1 2 4 8 16 --repeticoes 3
"""

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from comum import modelo  # noqa: E402
from comum.estatisticas import Estatisticas  # noqa: E402
from comum.parametros import ParametrosSimulacao  # noqa: E402
from distribuido.executar_local import executar_local  # noqa: E402
from paralelo.fakenews_paralelo import executar_simulacao as executar_paralela  # noqa: E402

PASTA = RAIZ / "experimentos" / "resultados"

CAMPOS = [
    "versao", "linhas", "workers", "geracoes", "repeticoes", "tempo_laco_s",
    "calculo_s", "comunicacao_s", "espera_s",
    "pct_calculo", "pct_comunicacao", "pct_espera", "soma_sobre_tempo",
    "bytes_por_worker_por_geracao", "desbalanceamento",
    "pico_espalhadores", "alcance_final",
]


def _console_seguro():
    """Evita que um acento fora da tabela do terminal derrube a medição."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")


def medir_uma(versao, parametros, workers):
    """Roda uma vez com estatísticas ligadas e devolve o perfil agregado."""
    est = Estatisticas(versao, parametros, workers)
    if versao == "paralela_processos":
        executar_paralela(parametros, workers, "processos", mostrar=False, estatisticas=est)
    elif versao in ("distribuida_local", "distribuida_bits"):
        executar_local(parametros, workers, bits=(versao == "distribuida_bits"),
                       mostrar=False, estatisticas=est)
    else:
        raise ValueError(f"versão sem perfil por worker: {versao}")

    perfis = est.por_trabalhador
    resumo = est.resumo()
    calculo = statistics.fmean(p["calculo_s"] for p in perfis)
    comunicacao = statistics.fmean(p["comunicacao_s"] for p in perfis)
    espera = statistics.fmean(p["espera_s"] for p in perfis)
    bytes_totais = sum(p["bytes_enviados"] for p in perfis)
    geracoes = max(1, len(est.geracoes))
    return {
        "tempo_laco_s": est.tempo_laco,
        "calculo_s": calculo,
        "comunicacao_s": comunicacao,
        "espera_s": espera,
        "bytes_por_worker_por_geracao": bytes_totais / max(1, workers) / geracoes,
        "geracoes": len(est.geracoes),
        "desbalanceamento": resumo.get("desbalanceamento", 1.0),
        "pico_espalhadores": resumo.get("pico_espalhadores"),
        "alcance_final": resumo.get("alcance_final"),
    }


def montar(versoes, tamanhos, workers, geracoes, limiar, repeticoes):
    """Executa todas as combinações e agrega pela mediana das repetições."""
    medidas = defaultdict(list)
    plano = [(v, t, w) for t in tamanhos for v in versoes for w in workers]
    for indice, (versao, tamanho, n) in enumerate(plano, start=1):
        parametros = ParametrosSimulacao(linhas=tamanho, colunas=tamanho,
                                         geracoes=geracoes, limiar=limiar)
        print(f"[{indice}/{len(plano)}] {versao:<20} {tamanho}x{tamanho} "
              f"workers={n:<3} ... ", end="", flush=True)
        try:
            for _ in range(repeticoes):
                medidas[(versao, tamanho, n)].append(
                    medir_uma(versao, parametros, n))
        except Exception as erro:  # noqa: BLE001 - uma configuração não derruba o resto
            print(f"FALHOU ({type(erro).__name__}: {erro})")
            continue
        amostras = medidas[(versao, tamanho, n)]
        print(f"calculo={statistics.fmean(a['calculo_s'] for a in amostras):.4f}s "
              f"comunic={statistics.fmean(a['comunicacao_s'] for a in amostras):.4f}s "
              f"espera={statistics.fmean(a['espera_s'] for a in amostras):.4f}s")

    linhas = []
    for (versao, tamanho, n), amostras in sorted(medidas.items()):
        def mediana(campo):
            return statistics.median(a[campo] for a in amostras)

        tempo = mediana("tempo_laco_s")
        calculo, comunicacao, espera = (mediana("calculo_s"),
                                        mediana("comunicacao_s"), mediana("espera_s"))
        soma = calculo + comunicacao + espera
        linhas.append({
            "versao": versao, "linhas": tamanho, "workers": n,
            "geracoes": amostras[0]["geracoes"], "repeticoes": len(amostras),
            "tempo_laco_s": round(tempo, 6),
            "calculo_s": round(calculo, 6),
            "comunicacao_s": round(comunicacao, 6),
            "espera_s": round(espera, 6),
            "pct_calculo": round(calculo / tempo * 100, 2) if tempo else None,
            "pct_comunicacao": round(comunicacao / tempo * 100, 2) if tempo else None,
            "pct_espera": round(espera / tempo * 100, 2) if tempo else None,
            "soma_sobre_tempo": round(soma / tempo, 3) if tempo else None,
            "bytes_por_worker_por_geracao": round(mediana("bytes_por_worker_por_geracao"), 1),
            "desbalanceamento": round(mediana("desbalanceamento"), 3),
            "pico_espalhadores": amostras[0]["pico_espalhadores"],
            "alcance_final": round(amostras[0]["alcance_final"], 4),
        })
    return linhas


def gerar_tabela(linhas):
    """Tabela Markdown do perfil de tempo, pronta para o relatório."""
    partes = ["# Perfil de tempo por worker", "",
              "Fases medidas dentro de cada worker (mediana das repetições). "
              "`soma/tempo` perto de 1,0 confirma que as três fases cobrem o laço.", "",
              "| Versão | Grade | *workers* | Tempo do laço (s) | Cálculo (s) | "
              "Comunicação (s) | Espera (s) | % cálculo | % comunicação | % espera | "
              "soma/tempo | Bytes/worker/geração | Desbalanceamento |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for l in linhas:
        partes.append(
            f"| {l['versao']} | {l['linhas']}² | {l['workers']} | {l['tempo_laco_s']:.4f} | "
            f"{l['calculo_s']:.4f} | {l['comunicacao_s']:.4f} | {l['espera_s']:.4f} | "
            f"{l['pct_calculo']} | {l['pct_comunicacao']} | {l['pct_espera']} | "
            f"{l['soma_sobre_tempo']} | {l['bytes_por_worker_por_geracao']} | "
            f"{l['desbalanceamento']} |")
    return "\n".join(partes)


def main(argv=None):
    """Lê os argumentos, mede os perfis e grava CSV + tabela."""
    _console_seguro()
    parser = argparse.ArgumentParser(description="Perfil de cálculo/comunicação/espera por worker")
    parser.add_argument("--linhas", type=int, nargs="+", default=[1000])
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    parser.add_argument("--versoes", nargs="+",
                        default=["paralela_processos", "distribuida_local", "distribuida_bits"])
    parser.add_argument("--geracoes", type=int, default=20)
    parser.add_argument("--limiar", type=int, default=2)
    parser.add_argument("--repeticoes", type=int, default=3)
    parser.add_argument("--saida", default=str(PASTA))
    args = parser.parse_args(argv)

    linhas = montar(args.versoes, args.linhas, sorted(set(args.workers)),
                    args.geracoes, args.limiar, args.repeticoes)
    if not linhas:
        print("Nada medido.")
        return 1

    pasta = Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    with open(pasta / "perfis.csv", "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)
    (pasta / "perfis.md").write_text(gerar_tabela(linhas), encoding="utf-8")

    print()
    print(gerar_tabela(linhas))
    print()
    print(f"CSV:    {pasta / 'perfis.csv'}")
    print(f"Tabela: {pasta / 'perfis.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
