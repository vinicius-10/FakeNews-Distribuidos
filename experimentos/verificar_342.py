"""
Reproduz as medições da seção 3.4.2 do trabalho — Tabelas 1 e 2.

O que cada tabela mede (conforme o texto do trabalho)
-----------------------------------------------------
Tabela 1: tempo do laço de gerações do **código fornecido** (o do professor,
`sequencial_original`, com `deepcopy` por geração) em três tamanhos de grade,
com 20 gerações, 5% de espalhadores e limiar 2, sem impressão. Mediana de
três repetições. Aferida num i9-12900F, Windows 11, Python 3.11.7.

Tabela 2: como o tempo de **uma** geração (1000×1000, mesmos parâmetros) se
divide entre varredura das células, cópia da grade e contagem de estados.
Mediana de cinco repetições após um aquecimento. Aferida num i7-13650HX,
Windows 11, Python 3.12.10.

A decomposição da Tabela 2 segue o que o texto descreve: o `deepcopy` acontece
dentro de `proxima_geracao` e o código fornecido não foi alterado, então a
cópia é medida **à parte**, sobre a mesma grade, e o tempo da varredura sai por
**diferença** (`proxima_geracao` − cópia). A contagem é medida isolada sobre a
grade nova. Os totais são divididos pelo número de gerações para dar "por
geração".

Versão do interpretador (importa, e muito)
------------------------------------------
O padrão de execução é **Python 3.12**, e o script avisa quando roda em outra
versão. A versão não é detalhe: em 3.12 o código do professor fica mais lento
que em 3.11, e o efeito **cresce com o tamanho da grade** — o custo por célula
vai de ~0,88 µs na grade de 500² a ~1,02 µs na de 2000² (+16%). Consequência:
a Tabela 1, publicada em 3.11.7, **não se reproduz em 3.12** (chega a +24% em
2000²), enquanto a Tabela 2, publicada em 3.12.10, reproduz dentro de 2%.
Registre sempre a versão junto do número.

Como usar
---------
    py -3.12 -m experimentos.verificar_342               # as duas tabelas
    py -3.12 -m experimentos.verificar_342 --tabela 1    # só a Tabela 1
    py -3.12 -m experimentos.verificar_342 --tabela 2    # só a Tabela 2

O resultado sai em `experimentos/resultados/secao-3.4.2.md`, com a comparação
lado a lado contra os valores publicados e o desvio percentual.
"""

import argparse
import platform
import statistics
import sys
import time
from copy import deepcopy
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sequencial import fakenews_sequencial_original as professor  # noqa: E402

# Valores publicados no trabalho (seção 3.4.2). Servem de referência para o
# desvio; não são usados em nenhum cálculo.
PUBLICADO_TABELA1 = {
    500: {"tempo": 4.16, "por_geracao": 0.208, "por_celula_us": 0.83},
    1000: {"tempo": 16.46, "por_geracao": 0.823, "por_celula_us": 0.82},
    2000: {"tempo": 65.88, "por_geracao": 3.294, "por_celula_us": 0.82},
}
PUBLICADO_TABELA2 = {
    "varredura": 0.638,
    "copia": 0.179,
    "contagem": 0.038,
    "total": 0.855,
}

GERACOES = 20
PERCENTUAL = 0.05
LIMIAR = 2
SEMENTE = 42

# Versão de Python de referência para as medições deste projeto: **3.12**.
# É a versão do ambiente do grupo e a que o artigo usou na Tabela 2. A Tabela 1
# do artigo foi medida em 3.11.7, então o desvio dela aqui inclui o efeito da
# troca de interpretador — não é só ruído de máquina.
VERSAO_PADRAO = "3.12"


def aviso_de_versao(versao=None):
    """
    Aviso a imprimir quando a medição não roda na versão de referência.

    Devolve None quando a versão é a padrão (3.12.x).
    """
    atual = versao or platform.python_version()
    if atual.split(".")[:2] == VERSAO_PADRAO.split("."):
        return None
    return (f"⚠️  Python {atual} — o padrão do projeto é {VERSAO_PADRAO}. "
            "O custo das etapas muda com o interpretador: em 3.12 a varredura "
            "pesa mais e a cópia menos do que em 3.11. Rode com 3.12 para "
            "comparar com a Tabela 2 do artigo.")



def _console_seguro():
    """Acentos fora da tabela do terminal não podem derrubar a medição."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")


def _mediana(valores):
    return statistics.median(valores)


def _desvio(novo, antigo):
    """Desvio percentual do novo valor em relação ao publicado."""
    if antigo in (None, 0) or novo is None:
        return None
    return (novo - antigo) / antigo * 100


def medir_tabela1(tamanhos, repeticoes=3, aquecimento=1):
    """
    Tempo do laço de gerações do código fornecido, por tamanho de grade.

    Usa as funções do original (`criar_grade` + `proxima_geracao` +
    `contar_estados`), que é exatamente o que a Tabela 1 mede.
    """
    resultado = {}
    for tamanho in tamanhos:
        print(f"  {tamanho}x{tamanho}: aquecimento + {repeticoes} repetições ... ",
              end="", flush=True)
        tempos = []
        geracoes_por_execucao = []
        for indice in range(aquecimento + repeticoes):
            grade = professor.criar_grade(tamanho, tamanho, PERCENTUAL, SEMENTE)
            inicio = time.perf_counter()
            geracoes = 0
            for geracao in range(1, GERACOES + 1):
                grade = professor.proxima_geracao(grade, LIMIAR)
                contagem = professor.contar_estados(grade)
                geracoes = geracao
                # Parada antecipada: o código fornecido para quando não há mais
                # espalhadores. Com limiar 2 e 5% isso não acontece em 20 gerações.
                if contagem[professor.ESPALHADOR] == 0:
                    break
            duracao = time.perf_counter() - inicio
            if indice >= aquecimento:
                tempos.append(duracao)
                geracoes_por_execucao.append(geracoes)
        mediana = _mediana(tempos)
        geracoes = int(_mediana(geracoes_por_execucao))
        celulas = tamanho * tamanho
        resultado[tamanho] = {
            "celulas": celulas,
            "tempo": mediana,
            "por_geracao": mediana / geracoes if geracoes else None,
            "por_celula_us": (mediana / geracoes / celulas * 1e6) if geracoes else None,
            "geracoes": geracoes,
            "repeticoes": len(tempos),
        }
        print(f"{mediana:.2f} s ({geracoes} gerações)")
    return resultado


def medir_tabela2(tamanho=1000, repeticoes=5, aquecimento=1):
    """
    Divisão do tempo de uma geração entre varredura, cópia e contagem.

    Em cada geração: mede o `deepcopy` à parte (sobre a mesma grade), mede
    `proxima_geracao` inteira e obtém a varredura por diferença; mede
    `contar_estados` isolada. Ao fim, divide os totais pelo número de gerações,
    porque a tabela publicada é "por geração".
    """
    print(f"  decomposição {tamanho}x{tamanho}: aquecimento + {repeticoes} repetições ... ",
          end="", flush=True)
    amostras = []
    for indice in range(aquecimento + repeticoes):
        grade = professor.criar_grade(tamanho, tamanho, PERCENTUAL, SEMENTE)
        varredura = copia = contagem_s = total = 0.0
        executadas = 0
        for _ in range(GERACOES):
            # 1) cópia medida à parte, sobre a mesma grade de entrada.
            inicio = time.perf_counter()
            deepcopy(grade)
            t_copia = time.perf_counter() - inicio

            # 2) a geração inteira (que faz o seu próprio deepcopy lá dentro).
            inicio = time.perf_counter()
            grade = professor.proxima_geracao(grade, LIMIAR)
            t_total = time.perf_counter() - inicio

            # 3) contagem dos estados sobre a grade nova.
            inicio = time.perf_counter()
            professor.contar_estados(grade)
            t_contagem = time.perf_counter() - inicio

            copia += t_copia
            total += t_total
            varredura += t_total - t_copia
            contagem_s += t_contagem
            executadas += 1

        if indice >= aquecimento and executadas:
            amostras.append({
                "varredura": varredura / executadas,
                "copia": copia / executadas,
                "contagem": contagem_s / executadas,
                "total": total / executadas,
            })
    resultado = {chave: _mediana([a[chave] for a in amostras])
                 for chave in ("varredura", "copia", "contagem", "total")}
    resultado["repeticoes"] = len(amostras)
    print(f"total {resultado['total']:.3f} s/geração")
    return resultado


def _tabela1_md(medido):
    """Monta a Tabela 1 em markdown, com a coluna de desvio."""
    linhas = [
        "| Grade | Células | Tempo (s) | Por geração (s) | Por célula e geração (µs) | Desvio do tempo |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for tamanho in sorted(medido):
        d = medido[tamanho]
        publicado = PUBLICADO_TABELA1.get(tamanho, {})
        desvio = _desvio(d["tempo"], publicado.get("tempo"))
        desvio_txt = "—" if desvio is None else f"{desvio:+.1f}%"
        linhas.append(
            f"| {tamanho}× {tamanho} | {d['celulas']:,} | {d['tempo']:.2f} | "
            f"{d['por_geracao']:.3f} | {d['por_celula_us']:.2f} | {desvio_txt} |")
    return "\n".join(linhas)


def _tabela2_md(medido):
    """Monta a Tabela 2 em markdown, com a coluna de desvio."""
    linhas = [
        "| Etapa | Por geração (s) | Participação (%) | Publicado (s) | Desvio |",
        "|---|---:|---:|---:|---:|",
    ]
    etapas = [("varredura", "Varredura das células"),
              ("copia", "Cópia da grade (deepcopy)"),
              ("contagem", "Contagem dos estados (contar_estados)"),
              ("total", "Total")]
    total = medido["total"] or 0
    for chave, rotulo in etapas:
        valor = medido[chave]
        participacao = (valor / total * 100) if total else 0
        publicado = PUBLICADO_TABELA2.get(chave)
        desvio = _desvio(valor, publicado)
        desvio_txt = "—" if desvio is None else f"{desvio:+.1f}%"
        linhas.append(f"| {rotulo} | {valor:.3f} | {participacao:.1f} | "
                      f"{publicado if publicado is not None else '—'} | {desvio_txt} |")
    return "\n".join(linhas)


def main(argv=None):
    """Roda as tabelas pedidas e grava o relatório da comparação."""
    _console_seguro()
    parser = argparse.ArgumentParser(
        description="Reproduz as medições da seção 3.4.2 (Tabelas 1 e 2)")
    parser.add_argument("--tabela", choices=("1", "2", "ambas"), default="ambas")
    parser.add_argument("--tamanhos", type=int, nargs="+", default=[500, 1000, 2000])
    parser.add_argument("--repeticoes", type=int, default=3,
                        help="repetições da Tabela 1 (o texto usa 3)")
    parser.add_argument("--repeticoes2", type=int, default=5,
                        help="repetições da Tabela 2 (o texto usa 5)")
    parser.add_argument("--saida", default=str(RAIZ / "experimentos" / "resultados"
                                               / "secao-3.4.2.md"))
    args = parser.parse_args(argv)

    ambiente = {
        "processador": platform.processor() or platform.machine(),
        "nucleos_logicos": __import__("os").cpu_count(),
        "sistema": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python": platform.python_version(),
        "implementacao": platform.python_implementation(),
    }
    print("=== VERIFICAÇÃO DA SEÇÃO 3.4.2 ===")
    for chave, valor in ambiente.items():
        print(f"{chave}: {valor}")
    print(f"parâmetros: {GERACOES} gerações, {PERCENTUAL:.0%} de espalhadores, "
          f"limiar {LIMIAR}, semente {SEMENTE}\n")
    aviso = aviso_de_versao(ambiente["python"])
    if aviso:
        print(aviso)
        print()

    relatorio = ["# Verificação da seção 3.4.2 — Medições", "",
                 "Reprodução das Tabelas 1 e 2 do trabalho nesta máquina, para conferir "
                 "se os resultados se mantêm.", ""]
    relatorio.append("## Ambiente")
    relatorio.append("")
    for chave, valor in ambiente.items():
        relatorio.append(f"- **{chave}**: {valor}")
    relatorio.append(f"- **parâmetros**: {GERACOES} gerações, {PERCENTUAL:.0%} de "
                     f"espalhadores, limiar {LIMIAR}, semente {SEMENTE}")
    relatorio.append("")

    tabela1 = tabela2 = None
    if args.tabela in ("1", "ambas"):
        inicio = time.perf_counter()
        tabela1 = medir_tabela1(args.tamanhos, args.repeticoes)
        duracao = time.perf_counter() - inicio
        print(f"  Tabela 1 pronta em {duracao:.0f} s\n")
        relatorio += ["## Tabela 1 — tempo do laço de gerações (código fornecido)", "",
                      f"Mediana de {args.repeticoes} repetições, após aquecimento. "
                      f"Medido em {duracao:.0f} s.", "",
                      _tabela1_md(tabela1), "",
                      f"Publicado: 4,16 s / 16,46 s / 65,88 s para 500², 1000² e 2000², "
                      f"com 0,82–0,83 µs por célula e geração.", ""]

    if args.tabela in ("2", "ambas"):
        inicio = time.perf_counter()
        tabela2 = medir_tabela2(1000, args.repeticoes2)
        duracao = time.perf_counter() - inicio
        print(f"  Tabela 2 pronta em {duracao:.0f} s\n")
        relatorio += ["## Tabela 2 — divisão do tempo de uma geração (1000×1000)", "",
                      f"Mediana de {args.repeticoes2} repetições, após aquecimento. "
                      f"Medido em {duracao:.0f} s.", "",
                      _tabela2_md(tabela2), "",
                      "A varredura é obtida por diferença (`proxima_geracao` − cópia "
                      "medida à parte), e a contagem é medida isolada — a mesma "
                      "metodologia descrita no texto.", ""]

    # Veredito: o que se manteve e o que mudou.
    relatorio += ["## Veredito", ""]
    if tabela1:
        desvios = [_desvio(tabela1[t]["tempo"], PUBLICADO_TABELA1[t]["tempo"])
                   for t in tabela1 if t in PUBLICADO_TABELA1]
        maior_desvio = max(abs(d) for d in desvios) if desvios else None
        por_celula = [tabela1[t]["por_celula_us"] for t in sorted(tabela1)]
        # Critério RELATIVO. A amplitude absoluta engana: 0,14 µs parece pouco,
        # mas sobre 0,88 µs é 16% de variação — e é justamente o que aparece em
        # Python 3.12 na grade maior, onde a localidade de cache piora.
        menor_celula, maior_celula = min(por_celula), max(por_celula)
        variacao_relativa = ((maior_celula - menor_celula) / menor_celula * 100
                             if menor_celula else 0.0)
        estavel = variacao_relativa <= 10.0
        lista_celula = ", ".join(f"{tamanho}={valor:.2f}"
                                 for tamanho, valor in zip(sorted(tabela1), por_celula))
        if maior_desvio is not None:
            relatorio.append(
                f"- **Tabela 1**: maior desvio {maior_desvio:.1f}% no tempo total em "
                f"relação ao publicado.")
        else:
            relatorio.append(
                "- **Tabela 1**: nenhum tamanho medido tem valor publicado "
                "(500, 1000 ou 2000) para comparar.")
        relatorio.append(
            f"  Custo por célula e geração: {lista_celula} µs — "
            f"{'permanece estável' if estavel else 'variou'} "
            f"({variacao_relativa:.0f}% entre o menor e o maior tamanho). "
            f"{'Confirma a linearidade em L·C que o texto afirma.' if estavel else 'A linearidade em L·C NÃO se confirmou neste ambiente: a grade maior ficou proporcionalmente mais cara (efeito de cache).'}")
    if tabela2:
        desvio_total = _desvio(tabela2["total"], PUBLICADO_TABELA2["total"])
        total = tabela2["total"] or 1
        relatorio.append(
            f"- **Tabela 2**: total de {tabela2['total']:.3f} s por geração contra "
            f"0,855 s publicados ({desvio_total:+.1f}%).")
        relatorio.append(
            f"  Participações medidas: varredura {tabela2['varredura'] / total * 100:.0f}%, "
            f"cópia {tabela2['copia'] / total * 100:.0f}% e "
            f"contagem {tabela2['contagem'] / total * 100:.0f}% "
            f"(publicado: 74,6% / 21,0% / 4,4%).")
        relatorio.append(
            "  A Tabela 2 do trabalho foi medida em **outra máquina** "
            "(i7-13650HX, Python 3.12.10); os valores absolutos não são diretamente "
            "comparáveis, mas a **proporção** entre as etapas deve se manter.")
    relatorio.append("")

    caminho = Path(args.saida)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(relatorio), encoding="utf-8")
    print(f"relatório: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
