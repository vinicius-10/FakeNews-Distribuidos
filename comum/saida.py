"""
Impressão no terminal, no mesmo formato da versão do professor.

Manter o formato permite comparar a saída das versões lado a lado.
"""

from comum.modelo import BOT, ESPALHADOR, IGNORANTE, INATIVO

SIMBOLOS = {IGNORANTE: ".", ESPALHADOR: "E", INATIVO: "N", BOT: "B"}


def imprimir_cabecalho(titulo, parametros, contagem, detalhes=()):
    """Imprime o cabeçalho com os parâmetros e a contagem inicial."""
    linhas, colunas = parametros.linhas, parametros.colunas
    print(f"=== SIMULAÇÃO {titulo} DE PROPAGAÇÃO DE FAKE NEWS ===")
    print(f"Tamanho da grade: {linhas} x {colunas} ({linhas * colunas:,}) pessoas)")
    print(f"Gerações: {parametros.geracoes}")
    print(f"Percentual inicial de espalhadores: {parametros.percentual_espalhadores * 100:.2f}% "
          f"({contagem[ESPALHADOR]:,} espalhadores reais)")
    print(f"Limiar de convencimento: {parametros.limiar} vizinhos")
    if parametros.resistencia is not None:
        print(f"Resistência individual: limiar sorteado entre {parametros.resistencia[0]} "
              f"e {parametros.resistencia[1]}")
    if contagem[BOT]:
        print(f"Bots: {contagem[BOT]:,}")
    for linha in detalhes:
        print(linha)
    print()


def imprimir_geracao(geracao, contagem):
    """Imprime a linha de estatísticas de uma geração."""
    texto = (f"Geração {geracao:03d} | "
             f"Ignorantes: {contagem[IGNORANTE]:>10,} | "
             f"Espalhadores: {contagem[ESPALHADOR]:>10,} | "
             f"Inativos: {contagem[INATIVO]:>10,}")
    if contagem[BOT]:
        texto += f" | Bots: {contagem[BOT]:>8,}"
    print(texto)


def imprimir_grade(plana, linhas, colunas, limite=30):
    """Mostra o canto superior esquerdo da grade (para grades pequenas)."""
    for i in range(min(linhas, limite)):
        inicio = (i + 1) * colunas
        # Cada símbolo seguido de um espaço, como o professor (inclusive o último).
        print("".join(SIMBOLOS[plana[inicio + j]] + " " for j in range(min(colunas, limite))))
    print()


def imprimir_resultado(tempo, contagem, total, tempo_total=None,
                       rotulo_total="Tempo incluindo criação de processos/threads"):
    """
    Imprime o resultado final, como o professor, com o tempo do laço.

    `rotulo_total` diz o que o `tempo_total` mede em cada versão (na
    distribuída ele começa depois que todos os workers conectam).
    """
    print()
    print("=== RESULTADO FINAL ===")
    print(f"Tempo total de execução: {tempo:.4f} segundos")
    if tempo_total is not None:
        print(f"{rotulo_total}: {tempo_total:.4f} segundos")
    print(f"Ignorantes finais: {contagem[IGNORANTE]:,} ({contagem[IGNORANTE] / total * 100:,.2f}%)")
    print(f"Espalhadores finais: {contagem[ESPALHADOR]:,} "
          f"({contagem[ESPALHADOR] / total * 100:,.2f}%)")
    print(f"Inativos finais: {contagem[INATIVO]:,} ({contagem[INATIVO] / total * 100:,.2f}%)")
    if contagem[BOT]:
        print(f"Bots: {contagem[BOT]:,} ({contagem[BOT] / total * 100:,.2f}%)")
