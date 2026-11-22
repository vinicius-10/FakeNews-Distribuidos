"""
Versão sequencial refatorada.

Faz o mesmo que o código do professor (fakenews_sequencial_original.py, que não
é alterado), mas usando o núcleo comum (comum/modelo.py): grade em vetor de
bytes com moldura e dois buffers alternados em vez de deepcopy a cada geração.

Serve para duas coisas:
- linha de base "1 worker" dos experimentos: o mesmo cálculo das versões
  paralela e distribuída, sem nenhum custo de processos ou rede;
- referência das melhorias do modelo (bots, resistência), que o código do
  professor não tem.

Uso: python -m sequencial.fakenews_sequencial --linhas 500 --colunas 500 --limiar 2
"""

import time

from comum import modelo
from comum.estatisticas import Estatisticas
from comum.parametros import novo_parser, parametros_de_argumentos, preparar_estado_inicial
from comum.saida import imprimir_cabecalho, imprimir_geracao, imprimir_grade, imprimir_resultado
from comum.visualizacao import Animacao


def executar_simulacao(parametros, mostrar=True, mostrar_grade=False, ao_fim_da_geracao=None,
                       estatisticas=None, animacao=None):
    """
    Executa a simulação inteira num único processo.

    ao_fim_da_geracao(geracao, grade) é chamado depois de cada geração com o
    vetor da grade (usado pelos testes e pela animação). Devolve um dicionário
    com a grade final, a contagem final, as gerações executadas e o tempo.
    """
    linhas, colunas = parametros.linhas, parametros.colunas
    atual, limiares = preparar_estado_inicial(parametros)
    nova = bytearray(len(atual))  # moldura de zeros já incluída
    contagem = modelo.contar_faixa(atual, colunas, 1, linhas + 1)

    if mostrar:
        imprimir_cabecalho("SEQUENCIAL (REFATORADA)", parametros, contagem)
    if animacao is not None:
        animacao.adicionar(0, atual)

    inicio = time.perf_counter()
    geracoes_executadas = 0
    for geracao in range(1, parametros.geracoes + 1):
        modelo.calcular_faixa(atual, nova, colunas, 1, linhas + 1, parametros.limiar, limiares)
        # Troca de buffers: a geração nova vira a atual. Só troca referências;
        # o buffer antigo será todo reescrito na próxima geração.
        atual, nova = nova, atual
        geracoes_executadas = geracao
        contagem = modelo.contar_faixa(atual, colunas, 1, linhas + 1)

        if mostrar:
            imprimir_geracao(geracao, contagem)
            if mostrar_grade:
                imprimir_grade(atual, linhas, colunas)
        if estatisticas is not None:
            estatisticas.registrar_geracao(geracao, contagem)
        if animacao is not None:
            animacao.adicionar(geracao, atual)
        if ao_fim_da_geracao is not None:
            ao_fim_da_geracao(geracao, bytes(atual))
        # Mesma parada do professor; bots contam como espalhadores, então com
        # bots a simulação só termina pelo número de gerações.
        if contagem[modelo.ESPALHADOR] + contagem[modelo.BOT] == 0:
            if mostrar:
                print("\nA propagação terminou: não há mais espalhadores.")
            break
    tempo = time.perf_counter() - inicio

    if estatisticas is not None:
        estatisticas.tempo_laco = tempo
        estatisticas.tempo_total = tempo
        # Um único "worker": todo o tempo é cálculo, sem comunicação nem espera.
        estatisticas.registrar_trabalhador(0, tempo, 0.0, 0.0)
    if mostrar:
        imprimir_resultado(tempo, contagem, linhas * colunas)
    return {"grade": bytes(atual), "contagem": contagem,
            "geracoes_executadas": geracoes_executadas, "tempo_laco": tempo}


def main(argv=None):
    """Lê os argumentos da linha de comando e executa."""
    parser = novo_parser("Simulação sequencial (refatorada) de propagação de fake news")
    args = parser.parse_args(argv)
    parametros = parametros_de_argumentos(args)
    estatisticas = Estatisticas("sequencial", parametros) if args.estatisticas else None
    animacao = (Animacao(parametros.linhas, parametros.colunas, "sequencial")
                if args.animacao else None)
    executar_simulacao(parametros, mostrar_grade=args.mostrar_grade,
                       estatisticas=estatisticas, animacao=animacao)
    if estatisticas is not None:
        estatisticas.imprimir_resumo()
        print(f"Estatísticas gravadas em {estatisticas.salvar(args.estatisticas)}")
    if animacao is not None:
        print(f"Animação gravada em {animacao.salvar(args.animacao)}")


if __name__ == "__main__":
    main()
