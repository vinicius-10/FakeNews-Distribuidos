"""
Executa a versão distribuída inteira numa máquina só: o coordenador neste
processo e os workers em processos separados, conversando por sockets em
127.0.0.1. Usado nos testes e para demonstrar a versão sem precisar de várias
máquinas. Atenção: em localhost a rede não é de verdade, então o tempo medido
não inclui a latência de uma rede física.

Uso: python -m distribuido.executar_local --workers 4 --linhas 500 --colunas 500 --limiar 2
"""

import multiprocessing as mp

from comum.estatisticas import Estatisticas
from comum.parametros import novo_parser, parametros_de_argumentos
from comum.visualizacao import Animacao
from distribuido import coordenador, protocolo, worker


def executar_local(parametros, workers=2, bits=False, mostrar=True, mostrar_grade=False,
                   ao_fim_da_geracao=None, verificar=False, estatisticas=None, animacao=None,
                   timeout=protocolo.TIMEOUT_PADRAO):
    """Sobe os workers locais, coordena a execução e devolve o resultado."""
    # Valida antes de criar processos, para um erro de parâmetro não deixar
    # workers esperando um coordenador que não vai existir.
    coordenador.validar_workers(parametros, workers)
    # Porta 0: o sistema escolhe uma porta livre (testes em paralelo não colidem).
    servidor = protocolo.criar_servidor("127.0.0.1", 0)
    porta = servidor.getsockname()[1]
    ctx = mp.get_context("spawn")  # spawn explícito: igual no Windows e no Linux
    processos = [ctx.Process(target=worker.executar_worker,
                             args=("127.0.0.1", porta, "127.0.0.1", timeout),
                             name=f"worker-{i}") for i in range(workers)]
    for processo in processos:
        processo.start()
    try:
        return coordenador.executar_coordenador(
            parametros, servidor, workers, bits, mostrar=mostrar, mostrar_grade=mostrar_grade,
            ao_fim_da_geracao=ao_fim_da_geracao, verificar=verificar,
            estatisticas=estatisticas, animacao=animacao, timeout=timeout)
    finally:
        servidor.close()
        for processo in processos:
            processo.join(timeout=10)
            if processo.is_alive():
                processo.terminate()


def main(argv=None):
    """Lê os argumentos e executa coordenador e workers locais."""
    parser = coordenador.adicionar_argumentos_distribuidos(
        novo_parser("Simulação distribuída com todos os workers nesta máquina"))
    args = parser.parse_args(argv)
    parametros = parametros_de_argumentos(args)
    estatisticas = (Estatisticas("distribuida_local", parametros, args.workers)
                    if args.estatisticas else None)
    animacao = (Animacao(parametros.linhas, parametros.colunas, "distribuída")
                if args.animacao else None)
    executar_local(parametros, args.workers, args.bits, mostrar_grade=args.mostrar_grade,
                   estatisticas=estatisticas, animacao=animacao, timeout=args.timeout)
    if estatisticas is not None:
        estatisticas.imprimir_resumo()
        print(f"Estatísticas gravadas em {estatisticas.salvar(args.estatisticas)}")
    if animacao is not None:
        print(f"Animação gravada em {animacao.salvar(args.animacao)}")


if __name__ == "__main__":
    main()
