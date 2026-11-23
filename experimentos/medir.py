"""
Medição de desempenho das versões sequencial, paralela e distribuída.

O que este script mede
----------------------
Para cada combinação (versão, tamanho da grade, número de trabalhadores) ele
executa a simulação 1 vez de aquecimento (descartada) e N vezes para valer,
e grava **uma linha por repetição** em CSV. A estatística usada na análise é a
mediana das repetições, calculada por `analisar.py` (regra do CONTRIBUTING:
aquecimento descartado + pelo menos 5 repetições + mediana).

Versões medidas
---------------
- `sequencial_original`: laço escrito com as funções do professor
  (`criar_grade`, `proxima_geracao`, `contar_estados`), com `deepcopy` por
  geração. É a linha de base do trabalho e a evidência da melhoria
  "grade compacta".
- `sequencial`: versão refatorada sobre `comum/modelo.py`.
- `paralela_processos`: `multiprocessing` com memória compartilhada.
- `paralela_threads`: mesmo laço com threads (mostra o efeito do GIL).
- `distribuida_local`: coordenador + workers por socket TCP em 127.0.0.1.
- `distribuida_bits`: a mesma versão distribuída com a melhoria "borda
  compactada em bits".

O que NÃO entra no tempo
------------------------
O tempo medido é o do **laço de gerações** (`tempo_laco`), igual nas três
versões: a grade inicial é gerada antes de começar a contar e, na paralela e na
distribuída, a criação de processos e as conexões também ficam de fora. O
`tempo_total` (com criação de processos/conexões) é gravado na mesma linha para
a análise de custo de inicialização.

Correção
--------
Cada execução grava o SHA-256 da grade final. Como todas as versões têm de
produzir a mesma grade, a análise confere os hashes contra o da sequencial e
denuncia qualquer divergência — o experimento também serve de teste de
equivalência em escala.

Uso
---
    python -m experimentos.medir                       # configuração padrão
    python -m experimentos.medir --rapido              # fumaça, roda em segundos
    python -m experimentos.medir --repeticoes 10
    python -m experimentos.medir --tamanhos 1000 2000 --workers 1 2 4 8 16

Os arquivos vão para `experimentos/resultados/` (ambiente.csv e medicoes.csv).
"""

import argparse
import csv
import hashlib
import os
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # permite rodar de qualquer diretório
    sys.path.insert(0, str(RAIZ))

from comum import modelo  # noqa: E402
from comum.parametros import ParametrosSimulacao  # noqa: E402
from distribuido.executar_local import executar_local  # noqa: E402
from paralelo.fakenews_paralelo import executar_simulacao as executar_paralela  # noqa: E402
from sequencial.fakenews_sequencial import executar_simulacao as executar_sequencial  # noqa: E402
from sequencial.fakenews_sequencial_original import (  # noqa: E402
    ESPALHADOR,
    contar_estados,
    criar_grade,
    proxima_geracao,
)

PASTA_RESULTADOS = RAIZ / "experimentos" / "resultados"

# Versões com um único trabalhador (não faz sentido variar o número).
VERSOES_SERIAIS = ("sequencial_original", "sequencial")
# Versões em que o número de trabalhadores varia.
VERSOES_PARALELAS = ("paralela_processos", "paralela_threads",
                     "distribuida_local", "distribuida_bits")

CAMPOS = [
    "versao", "modo", "workers", "linhas", "colunas", "geracoes_pedidas",
    "geracoes_executadas", "limiar", "percentual", "repeticao",
    "tempo_laco_s", "tempo_total_s", "hash_grade",
    "ignorantes", "espalhadores", "inativos", "bots",
]

# Condição padrão de medição registrada em ambiente.csv, conforme a checklist
# de experimentos do grupo (hardware + condição da medição).
AMBIENTE_PADRAO = ("desktop na tomada, demais programas fechados; versão distribuída "
                   "em localhost (sem rede física)")


def _console_seguro():
    """
    Impede que um acento fora da tabela do terminal derrube a medição.

    No Windows o console costuma usar cp1252; os arquivos saem sempre em UTF-8.
    """
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")


# ---------------------------------------------------------------------------
# Ambiente: o CONTRIBUTING exige registrar a máquina de cada medição
# ---------------------------------------------------------------------------

def descrever_ambiente(override_cpu=None, override_fisicos=None, ambiente=None):
    """
    Coleta os dados da máquina que vão na tabela de configuração experimental.

    Núcleos físicos não existem na biblioteca padrão: usa `psutil` se estiver
    instalado e, se não estiver, aceita o valor informado à mão pelos argumentos
    `--cpu` e `--nucleos-fisicos` (é o que vai para o relatório).

    `ambiente` registra a condição da medição (na tomada? local ou rede?), que a
    checklist de experimentos do grupo pede junto com o hardware: o mesmo
    processador rende bem menos na bateria.
    """
    fisicos = override_fisicos
    if fisicos is None:
        try:
            import psutil  # opcional
            fisicos = psutil.cpu_count(logical=False)
        except ImportError:
            fisicos = ""
    memoria = ""
    try:
        import psutil  # opcional
        memoria = round(psutil.virtual_memory().total / 1024 ** 3, 1)
    except ImportError:
        memoria = ""
    return {
        "processador": override_cpu or platform.processor() or platform.machine(),
        "nucleos_fisicos": fisicos,
        "nucleos_logicos": os.cpu_count(),
        "memoria_gb": memoria,
        "sistema": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python": platform.python_version(),
        "implementacao": platform.python_implementation(),
        "ambiente": ambiente or AMBIENTE_PADRAO,
    }


# ---------------------------------------------------------------------------
# Execução de uma repetição de cada versão
# ---------------------------------------------------------------------------

def _resumir(resultado, tempo_total):
    """Transforma o retorno de qualquer versão na linha padrão do CSV."""
    contagem = resultado["contagem"]
    return {
        "tempo_laco_s": resultado["tempo_laco"],
        "tempo_total_s": tempo_total,
        "geracoes_executadas": resultado["geracoes_executadas"],
        "hash_grade": hashlib.sha256(bytes(resultado["grade"])).hexdigest(),
        "ignorantes": contagem[modelo.IGNORANTE],
        "espalhadores": contagem[modelo.ESPALHADOR],
        "inativos": contagem[modelo.INATIVO],
        "bots": contagem[modelo.BOT],
    }


def executar_original(parametros):
    """
    Roda o laço do professor sem imprimir nada e devolve o mesmo formato.

    Usa as funções do arquivo original (que não é alterado) para que a linha de
    base dos experimentos seja exatamente o código entregue na disciplina.
    """
    grade = criar_grade(parametros.linhas, parametros.colunas,
                        parametros.percentual_espalhadores, parametros.semente)
    inicio = time.perf_counter()
    geracoes = 0
    for geracao in range(1, parametros.geracoes + 1):
        grade = proxima_geracao(grade, parametros.limiar)
        contagem = contar_estados(grade)
        geracoes = geracao
        if contagem[ESPALHADOR] == 0:
            break
    tempo = time.perf_counter() - inicio
    contagem = contar_estados(grade)
    return {
        "tempo_laco": tempo,
        "tempo_total": tempo,
        "geracoes_executadas": geracoes,
        "grade": bytes(modelo.grade_para_plana(grade)),
        "contagem": [contagem[modelo.IGNORANTE], contagem[modelo.ESPALHADOR],
                     contagem[modelo.INATIVO], 0],
    }


def executar_uma(versao, parametros, workers, timeout):
    """Executa uma vez a versão pedida e devolve a linha de medição."""
    if versao == "sequencial_original":
        resultado = executar_original(parametros)
        return _resumir(resultado, resultado["tempo_total"])
    if versao == "sequencial":
        resultado = executar_sequencial(parametros, mostrar=False)
        return _resumir(resultado, resultado["tempo_total"])
    if versao == "paralela_processos":
        resultado = executar_paralela(parametros, workers, "processos", mostrar=False,
                                      timeout=timeout)
        return _resumir(resultado, resultado["tempo_total"])
    if versao == "paralela_threads":
        resultado = executar_paralela(parametros, workers, "threads", mostrar=False,
                                      timeout=timeout)
        return _resumir(resultado, resultado["tempo_total"])
    if versao in ("distribuida_local", "distribuida_bits"):
        resultado = executar_local(parametros, workers, bits=(versao == "distribuida_bits"),
                                   mostrar=False, timeout=timeout)
        return _resumir(resultado, resultado["tempo_total"])
    raise ValueError(f"versão desconhecida: {versao}")


# ---------------------------------------------------------------------------
# Plano de medição
# ---------------------------------------------------------------------------

def montar_plano(tamanhos, workers, versoes):
    """
    Monta a lista de (versão, tamanho, workers) a medir.

    As versões seriais aparecem uma vez por tamanho; as paralelas, uma vez por
    (tamanho, número de trabalhadores).
    """
    plano = []
    for tamanho in tamanhos:
        for versao in versoes:
            if versao in VERSOES_SERIAIS:
                plano.append((versao, tamanho, 1))
            else:
                for n in workers:
                    plano.append((versao, tamanho, n))
    return plano


def medir(plano, parametros_base, repeticoes, aquecimento, timeout, saida):
    """Executa o plano inteiro e grava o CSV de medições."""
    linhas = []
    total = len(plano)
    for indice, (versao, tamanho, workers) in enumerate(plano, start=1):
        parametros = ParametrosSimulacao(
            linhas=tamanho, colunas=tamanho,
            geracoes=parametros_base.geracoes,
            percentual_espalhadores=parametros_base.percentual_espalhadores,
            limiar=parametros_base.limiar, semente=parametros_base.semente,
        )
        rotulo = f"[{indice}/{total}] {versao:<20} {tamanho}x{tamanho} workers={workers}"
        print(f"{rotulo} ... ", end="", flush=True)
        comeco = time.perf_counter()
        try:
            for _ in range(aquecimento):
                executar_uma(versao, parametros, workers, timeout)
            for repeticao in range(1, repeticoes + 1):
                medida = executar_uma(versao, parametros, workers, timeout)
                linhas.append({
                    "versao": versao,
                    "modo": "threads" if versao.endswith("threads") else
                            ("bits" if versao.endswith("bits") else
                             ("processos" if versao.endswith("processos") else "serial")),
                    "workers": workers, "linhas": tamanho, "colunas": tamanho,
                    "geracoes_pedidas": parametros.geracoes,
                    "limiar": parametros.limiar,
                    "percentual": parametros.percentual_espalhadores,
                    "repeticao": repeticao,
                    **medida,
                })
        except Exception as erro:  # noqa: BLE001 - uma configuração não derruba o resto
            print(f"FALHOU ({erro})")
            continue
        # Mediana parcial só para acompanhar o andamento no terminal.
        tempos = [l["tempo_laco_s"] for l in linhas[-repeticoes:]]
        print(f"mediana {statistics.median(tempos):.4f} s "
              f"({time.perf_counter() - comeco:.1f} s no total)")
        # Grava a cada configuração: se a execução for interrompida, o que já foi
        # medido não se perde.
        gravar_csv(saida, linhas)
    return linhas


def gravar_csv(caminho, linhas):
    """Grava as medições em CSV (UTF-8, newline="" para o Windows)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def gravar_ambiente(ambiente, caminho):
    """Grava a configuração da máquina em CSV, uma linha por campo."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["item", "valor"])
        escritor.writerows(ambiente.items())
    return caminho


def main(argv=None):
    """Lê os argumentos e roda a bateria de medições."""
    _console_seguro()
    parser = argparse.ArgumentParser(
        description="Mede o desempenho das versões da simulação de fake news")
    parser.add_argument("--tamanhos", type=int, nargs="+", default=[1000, 2000],
                        help="lados das grades quadradas (padrão: 1000 2000)")
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4, 8, 16],
                        help="números de trabalhadores das versões paralelas")
    parser.add_argument("--versoes", nargs="+",
                        default=list(VERSOES_SERIAIS + VERSOES_PARALELAS),
                        help="versões a medir")
    parser.add_argument("--geracoes", type=int, default=20)
    parser.add_argument("--limiar", type=int, default=2,
                        help="limiar de convencimento (o padrão do professor, 3, "
                             "mata a simulação em ~3 gerações e não dá tempo de medir)")
    parser.add_argument("--percentual", type=float, default=0.05)
    parser.add_argument("--repeticoes", type=int, default=5)
    parser.add_argument("--aquecimento", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--saida", default=str(PASTA_RESULTADOS / "medicoes.csv"))
    parser.add_argument("--cpu", help="nome do processador para o relatório")
    parser.add_argument("--nucleos-fisicos", type=int,
                        help="núcleos físicos (se o psutil não estiver instalado)")
    parser.add_argument("--ambiente",
                        help="condição da medição (ex.: 'notebook na tomada; rede real'), "
                             "gravada em ambiente.csv junto com o hardware")
    parser.add_argument("--rapido", action="store_true",
                        help="bateria de fumaça: grades pequenas e poucas repetições")
    args = parser.parse_args(argv)

    if args.rapido:
        args.tamanhos = [200, 400]
        args.workers = [1, 2, 4]
        args.repeticoes = 2
        args.geracoes = 5

    parametros_base = ParametrosSimulacao(geracoes=args.geracoes, limiar=args.limiar,
                                          percentual_espalhadores=args.percentual)
    ambiente = descrever_ambiente(args.cpu, args.nucleos_fisicos, args.ambiente)
    gravar_ambiente(ambiente, PASTA_RESULTADOS / "ambiente.csv")

    plano = montar_plano(args.tamanhos, sorted(set(args.workers)), args.versoes)
    print("=== MEDIÇÃO DE DESEMPENHO ===")
    for chave, valor in ambiente.items():
        print(f"{chave}: {valor}")
    print(f"Configurações: {len(plano)} | repetições: {args.repeticoes} "
          f"(+{args.aquecimento} de aquecimento) | gerações: {args.geracoes} | "
          f"limiar: {args.limiar}")
    print(f"Saída: {args.saida}\n")

    comeco = time.perf_counter()
    linhas = medir(plano, parametros_base, args.repeticoes, args.aquecimento,
                   args.timeout, args.saida)
    print(f"\n{len(linhas)} medições gravadas em {args.saida} "
          f"em {time.perf_counter() - comeco:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
