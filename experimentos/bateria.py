"""
Bateria de experimentos: varia **parâmetros e porcentagens** nas três versões.

Por que este script existe
--------------------------
O `experimentos/medir.py` mede desempenho variando tamanho da grade, número de
trabalhadores e versão — mas `--percentual` e `--limiar` entram como valor único,
fixo para a bateria inteira. A pergunta "a taxa inicial de espalhadores e o limiar
de convencimento mudam o custo de cada versão?" não tem como ser respondida lá.

Aqui a grade de cenários é o produto cartesiano:

    percentuais  ×  limiares  ×  tamanhos  ×  versões  ×  trabalhadores

e cada célula roda aquecimento + N repetições. O que sai:

- `medicoes.csv` — uma linha por repetição, **no mesmo formato do `medir.py`**
  (`medir.CAMPOS`), então `analisar.carregar` e as métricas continuam valendo;
- `resumo.md` — tabela por cenário com mediana, desvio, speedup e eficiência,
  mais o veredito de equivalência de cada célula;
- `cenarios.json` — os mesmos cenários prontos para o setup de três máquinas
  (`distribuido/rede/`), que roda exatamente as mesmas configurações na rede real.

Por que não dá para usar `analisar.agrupar` direto no CSV inteiro
-----------------------------------------------------------------
`analisar.agrupar` agrupa por `(versão, linhas, workers)` e
`analisar.verificar_equivalencia` compara por `linhas`. Os dois **ignoram
`percentual` e `limiar`**, porque no `medir.py` esses campos são constantes.
Numa bateria que varia os dois, isso misturaria cenários diferentes na mesma
mediana e acusaria divergência falsa de hashes (grades de percentuais diferentes
são diferentes por definição). A solução aqui é fatiar o CSV por cenário antes de
chamar as funções — a análise é a mesma, só que aplicada ao subconjunto certo.

Custo de cada versão
--------------------
`tempo_laco` é a métrica principal: a grade inicial é gerada antes de começar a
contar, e na paralela/distribuída a criação de processos e as conexões ficam
fora. O `tempo_total` vai junto só para diagnóstico. Atenção: na distribuída ele
começa depois que todos os workers conectam, então **não é comparável** com o
`tempo_total` da paralela — comparar versões por `tempo_laco`.

Uso
---
    python -m experimentos.bateria --rapida

    # a bateria completa do enunciado: 4 porcentagens × 3 limiares
    python -m experimentos.bateria \\
        --percentuais 0.01 0.05 0.10 0.20 --limiares 1 2 3 \\
        --tamanhos 500 1000 --geracoes 20 --workers 1 2 4 --repeticoes 3

    # só listar o que rodaria (não executa nada)
    python -m experimentos.bateria --simular

    # exportar os cenários para rodar nas 3 máquinas
    python -m experimentos.bateria --rapida --exportar-cenarios cenarios.json
"""

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from . import analisar
from . import medir

# Versões que entram por padrão. A `sequencial_original` fica de fora porque
# faz `deepcopy` a cada geração e domina o tempo total da bateria; quem quiser
# a linha de base do professor usa `--versoes ... sequencial_original`.
VERSOES_PADRAO = ("sequencial", "paralela_processos", "paralela_threads",
                  "distribuida_local", "distribuida_bits")

PASTA_PADRAO = Path(__file__).resolve().parent / "resultados" / "bateria"


@dataclass(frozen=True)
class Cenario:
    """Uma célula da grade: uma configuração de simulação."""

    percentual: float
    limiar: int
    tamanho: int

    @property
    def nome(self):
        """Identificador curto para tabelas e nomes de arquivo."""
        return f"p{self.percentual:g}_l{self.limiar}_{self.tamanho}x{self.tamanho}"

    def como_dict(self):
        """Forma serializável (vai para o JSON das 3 máquinas)."""
        return {"linhas": self.tamanho, "colunas": self.tamanho,
                "percentual": self.percentual, "limiar": self.limiar}


def montar_cenarios(percentuais, limiares, tamanhos):
    """
    Produto cartesiano percentual × limiar × tamanho, em ordem determinística.

    A ordem importa: os cenários são gravados e retomados por posição, e a
    execução tem de ser reprodutível entre máquinas.
    """
    return [Cenario(percentual=p, limiar=l, tamanho=t)
            for p in percentuais for l in limiares for t in tamanhos]


def montar_plano(cenarios, versoes, workers):
    """
    Expande os cenários em configurações executáveis.

    As versões seriais rodam uma vez por cenário; as paralelas, uma vez por
    número de trabalhadores — mesma regra do `medir.montar_plano`.
    """
    plano = []
    for cenario in cenarios:
        for versao in versoes:
            if versao in medir.VERSOES_SERIAIS:
                plano.append((cenario, versao, 1))
            else:
                for n in workers:
                    plano.append((cenario, versao, n))
    return plano


def estimar(plano, repeticoes, aquecimento):
    """Número de execuções que a bateria fará (para avisar antes de começar)."""
    return len(plano) * (repeticoes + aquecimento)


def medir_plano(plano, geracoes, semente, repeticoes, aquecimento, timeout, saida):
    """
    Executa o plano inteiro, reaproveitando `medir.executar_uma`.

    Reaproveitar a execução (em vez de reimplementar o laço de cada versão) é o
    que garante que a bateria meça exatamente o mesmo código que os outros
    experimentos e os testes de equivalência usam.
    """
    linhas = []
    total = len(plano)
    for indice, (cenario, versao, workers) in enumerate(plano, start=1):
        parametros = medir.ParametrosSimulacao(
            linhas=cenario.tamanho, colunas=cenario.tamanho,
            geracoes=geracoes, percentual_espalhadores=cenario.percentual,
            limiar=cenario.limiar, semente=semente,
        )
        rotulo = (f"[{indice}/{total}] {versao:<20} {cenario.nome:<20} "
                  f"workers={workers}")
        print(f"{rotulo} ... ", end="", flush=True)
        comeco = time.perf_counter()
        try:
            for _ in range(aquecimento):
                medir.executar_uma(versao, parametros, workers, timeout)
            for repeticao in range(1, repeticoes + 1):
                medida = medir.executar_uma(versao, parametros, workers, timeout)
                linhas.append({
                    "versao": versao,
                    "modo": "threads" if versao.endswith("threads") else
                            ("bits" if versao.endswith("bits") else
                             ("processos" if versao.endswith("processos") else "serial")),
                    "workers": workers,
                    "linhas": cenario.tamanho,
                    "colunas": cenario.tamanho,
                    "geracoes_pedidas": geracoes,
                    "limiar": cenario.limiar,
                    "percentual": cenario.percentual,
                    "repeticao": repeticao,
                    **medida,
                })
        except Exception as erro:  # noqa: BLE001 - uma célula não derruba a bateria
            print(f"FALHOU ({type(erro).__name__}: {erro})")
            continue
        tempos = [l["tempo_laco_s"] for l in linhas[-repeticoes:]]
        print(f"mediana {statistics.median(tempos):.4f} s "
              f"({time.perf_counter() - comeco:.1f} s)")
        # Grava a cada configuração: interromper não perde o que já foi medido.
        medir.gravar_csv(saida, linhas)
    return linhas


def fatiar_por_cenario(linhas, cenarios):
    """
    Separa as medições por cenário antes de analisar.

    Sem isso, `analisar.agrupar` juntaria percentuais e limiares diferentes sob a
    mesma chave (versão, tamanho, workers) e a mediana sairia da mistura.
    """
    fatias = {}
    for cenario in cenarios:
        fatias[cenario] = [
            linha for linha in linhas
            if linha["limiar"] == cenario.limiar
            and abs(linha["percentual"] - cenario.percentual) < 1e-12
            and linha["linhas"] == cenario.tamanho
        ]
    return fatias


def resumir_cenario(linhas):
    """
    Mediana por (versão, trabalhadores) e as métricas derivadas, dentro de um cenário.

    Devolve um dicionário ordenado por versão/trabalhadores. A referência do
    speedup é a `sequencial` do mesmo cenário: comparar versões entre cenários
    diferentes não tem sentido (a quantidade de trabalho muda).
    """
    resumo = analisar.agrupar(linhas)
    referencia = resumo.get(("sequencial", linhas[0]["linhas"], 1)) if linhas else None
    base = referencia["mediana"] if referencia else None

    saida = []
    for (versao, tamanho, workers), dados in sorted(resumo.items()):
        mediana = dados["mediana"]
        s = analisar.speedup(base, mediana) if base else None
        saida.append({
            "versao": versao,
            "workers": workers,
            "mediana": mediana,
            "desvio": dados["desvio"],
            "repeticoes": dados["repeticao"],
            "speedup": s,
            "eficiencia": analisar.eficiencia(s, workers) if s is not None else None,
            "mediana_total": dados["mediana_total"],
            "geracoes": dados["linha"]["geracoes_executadas"],
        })
    return saida


def _num(valor, casas=2):
    """Formata número tolerando None (célula sem referência de speedup)."""
    if valor is None:
        return "—"
    return f"{valor:,.{casas}f}"


def gerar_relatorio(linhas, cenarios, versoes, repeticoes=None):
    """
    Monta o `resumo.md`: uma seção por cenário, com tabela e veredito.

    A equivalência é conferida **dentro do cenário**: o hash da grade só pode ser
    comparado entre execuções dos mesmos parâmetros.
    """
    fatias = fatiar_por_cenario(linhas, cenarios)
    partes = ["# Bateria de experimentos — resumo", ""]
    partes.append("Mediana do tempo do laço por configuração. Speedup contra a "
                  "`sequencial` do mesmo cenário.")
    partes.append("")
    # Com uma repetição só, um outlier de agendamento do sistema infla o speedup
    # de forma absurda (já vi 2,15 com um único worker). O número vira indicativo,
    # não resultado — e quem lê a tabela precisa saber disso.
    if repeticoes is not None and repeticoes < 3:
        partes.append(f"> ⚠️ **{repeticoes} repetição(ões):** os tempos são "
                      "indicativos. Use `--repeticoes 3` ou mais e a mediana "
                      "para números de relatório.")
        partes.append("")

    total_divergencias = 0
    for cenario in cenarios:
        fatia = fatias[cenario]
        if not fatia:
            continue
        ok, divergencias, _ = analisar.verificar_equivalencia(fatia)
        total_divergencias += len(divergencias)

        partes.append(f"## {cenario.nome}")
        partes.append("")
        partes.append(f"- percentual de espalhadores: **{cenario.percentual:.2%}**")
        partes.append(f"- limiar: **{cenario.limiar}**")
        partes.append(f"- grade: **{cenario.tamanho} × {cenario.tamanho}**")
        partes.append("")
        partes.append("| versão | workers | mediana (s) | desvio (s) | speedup | eficiência | gerações |")
        partes.append("|---|---:|---:|---:|---:|---:|---:|")
        for item in resumir_cenario(fatia):
            partes.append(
                f"| `{item['versao']}` | {item['workers']} | "
                f"{_num(item['mediana'], 4)} | {_num(item['desvio'], 4)} | "
                f"{_num(item['speedup'])} | {_num(item['eficiencia'])} | "
                f"{item['geracoes']} |")
        partes.append("")
        if ok:
            partes.append("**Equivalência:** todas as versões produziram a mesma grade final. ✅")
        else:
            partes.append(f"**Equivalência:** ⚠️ {len(divergencias)} divergência(s)")
            for versao, tamanho, workers, achado, esperado in divergencias:
                partes.append(f"- `{versao}` ({tamanho}×{tamanho}, workers={workers}): "
                              f"hash {achado} ≠ esperado {esperado}")
        partes.append("")

    partes.append("## Veredito geral")
    partes.append("")
    if total_divergencias == 0:
        partes.append("Todas as células fecharam com a mesma grade da sequencial — "
                      "bateria válida para o relatório.")
    else:
        partes.append(f"⚠️ **{total_divergencias} divergência(s) de hash.** "
                      "Investigar antes de usar os números.")
    partes.append("")
    partes.append("> `tempo_laco` é a métrica comparável entre versões. "
                  "O `tempo_total` da distribuída começa depois que os workers "
                  "conectam, então não serve para comparar com a paralela.")
    partes.append("")
    return "\n".join(partes), total_divergencias


def exportar_cenarios(cenarios, versoes, workers, geracoes, semente, caminho):
    """
    Grava os cenários em JSON para o setup de três máquinas consumir.

    Só vai o que a rede precisa reproduzir: parâmetros da simulação e a lista de
    configurações medidas. O setup de 3 máquinas roda o **mesmo** cenário com o
    coordenador e os workers reais, e a comparação local × rede fica honesta.
    """
    dados = {
        "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
        "semente": semente,
        "geracoes": geracoes,
        "versoes_locais": list(versoes),
        "workers": list(workers),
        "cenarios": [
            {**cenario.como_dict(), "geracoes": geracoes, "semente": semente}
            for cenario in cenarios
        ],
    }
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    return caminho


def main(argv=None):
    """Lê os argumentos, monta o plano e roda a bateria."""
    medir._console_seguro()
    parser = argparse.ArgumentParser(
        description="Bateria de experimentos variando parâmetros e porcentagens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--percentuais", type=float, nargs="+",
                        default=[0.01, 0.05, 0.10],
                        help="frações iniciais de espalhadores (padrão: 0.01 0.05 0.10)")
    parser.add_argument("--limiares", type=int, nargs="+", default=[1, 2, 3],
                        help="limiares de convencimento (padrão: 1 2 3)")
    parser.add_argument("--tamanhos", type=int, nargs="+", default=[300, 600],
                        help="lados das grades quadradas (padrão: 300 600)")
    parser.add_argument("--versoes", nargs="+", default=list(VERSOES_PADRAO),
                        help="versões a medir")
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4],
                        help="números de trabalhadores das versões paralelas")
    parser.add_argument("--geracoes", type=int, default=20)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--repeticoes", type=int, default=3)
    parser.add_argument("--aquecimento", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--saida", default=str(PASTA_PADRAO),
                        help="pasta de saída (CSV, resumo e ambiente)")
    parser.add_argument("--exportar-cenarios", metavar="ARQ.json",
                        help="grava os cenários em JSON para o setup de 3 máquinas")
    parser.add_argument("--cpu", help="nome do processador para o relatório")
    parser.add_argument("--nucleos-fisicos", type=int,
                        help="núcleos físicos (se o psutil não estiver instalado)")
    parser.add_argument("--ambiente",
                        help="condição da medição, gravada em ambiente.csv")
    parser.add_argument("--simular", action="store_true",
                        help="só monta e mostra o plano; não executa nada")
    parser.add_argument("--rapida", action="store_true",
                        help="fumaça: 2 percentuais, 2 limiares, 1 tamanho, 1 repetição")
    args = parser.parse_args(argv)

    if args.rapida:
        args.percentuais = [0.01, 0.10]
        args.limiares = [1, 3]
        args.tamanhos = [200]
        args.repeticoes = 1
        args.geracoes = 5

    for valor in args.percentuais:
        if not 0 < valor <= 1:
            parser.error(f"--percentuais precisa ficar em (0, 1]; recebido {valor}")
    for valor in args.limiares:
        if not 0 <= valor <= 9:
            parser.error(f"--limiares vai de 0 a 9; recebido {valor}")

    cenarios = montar_cenarios(args.percentuais, args.limiares, args.tamanhos)
    plano = montar_plano(cenarios, args.versoes, sorted(set(args.workers)))
    execucoes = estimar(plano, args.repeticoes, args.aquecimento)

    ambiente = medir.descrever_ambiente(args.cpu, args.nucleos_fisicos, args.ambiente)
    print("=== BATERIA DE EXPERIMENTOS ===")
    for chave, valor in ambiente.items():
        print(f"{chave}: {valor}")
    print(f"cenários: {len(cenarios)} | configurações: {len(plano)} | "
          f"execuções: {execucoes} (repetições {args.repeticoes} + "
          f"aquecimento {args.aquecimento}) | gerações: {args.geracoes}")
    print(f"percentuais: {args.percentuais} | limiares: {args.limiares} | "
          f"tamanhos: {args.tamanhos}")
    print(f"saída: {args.saida}\n")
    if args.repeticoes < 3:
        print("⚠️  Menos de 3 repetições: os tempos servem para fumaça, não para o "
              "relatório.\n   O mesmo worker isolado já apareceu 2x mais rápido que a "
              "sequencial por\n   causa de um único outlier. Use --repeticoes 3 ou mais.\n")

    if args.simular:
        print("Plano (--simular, nada foi executado):")
        for cenario, versao, workers in plano:
            print(f"  {cenario.nome:<20} {versao:<20} workers={workers} "
                  f"geracoes={args.geracoes}")
        if args.exportar_cenarios:
            caminho = exportar_cenarios(cenarios, args.versoes, sorted(set(args.workers)),
                                        args.geracoes, args.semente, args.exportar_cenarios)
            print(f"\ncenários exportados para {caminho}")
        return 0

    pasta = Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    medir.gravar_ambiente(ambiente, pasta / "ambiente.csv")
    csv_saida = pasta / "medicoes.csv"

    comeco = time.perf_counter()
    linhas = medir_plano(plano, args.geracoes, args.semente, args.repeticoes,
                         args.aquecimento, args.timeout, csv_saida)
    duracao = time.perf_counter() - comeco

    relatorio, divergencias = gerar_relatorio(linhas, cenarios, args.versoes,
                                              repeticoes=args.repeticoes)
    (pasta / "resumo.md").write_text(relatorio, encoding="utf-8")

    caminho_json = None
    if args.exportar_cenarios:
        caminho_json = exportar_cenarios(cenarios, args.versoes, sorted(set(args.workers)),
                                         args.geracoes, args.semente, args.exportar_cenarios)

    print(f"\n{len(linhas)} medições em {duracao:.1f} s")
    print(f"CSV:      {csv_saida}")
    print(f"resumo:   {pasta / 'resumo.md'}")
    if caminho_json:
        print(f"cenários: {caminho_json}")
    if divergencias:
        print(f"\n⚠️ {divergencias} divergência(s) de hash — veja o resumo antes de usar os números.")
        return 1
    print("\nTodas as versões fecharam com a mesma grade da sequencial.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
