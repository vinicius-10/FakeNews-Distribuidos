"""
Coordenador da versão distribuída.

Papel do coordenador:
1. aceita a conexão dos P workers;
2. gera a grade inicial uma única vez (semente 42) e envia a cada worker só a
   sua faixa, junto com o endereço do vizinho de baixo;
3. a cada geração, recebe a contagem de estados de cada faixa, soma (redução
   global), imprime e decide se a simulação continua;
4. no fim, junta as faixas na grade final e o perfil de tempo de cada worker.

As bordas (halo) NÃO passam pelo coordenador: vão direto de worker para
worker. Se passassem, o coordenador receberia e reenviaria 2(P-1) linhas por
geração e viraria um gargalo serial.

Uso (numa máquina):  python -m distribuido.coordenador --workers 4 --porta 5000
Uso (entre máquinas): python -m distribuido.coordenador --host 0.0.0.0 --workers 4
e, em cada máquina:   python -m distribuido.worker --coordenador IP:5000 --escutar 0.0.0.0
"""

import time

from comum import modelo
from comum.estatisticas import Estatisticas
from comum.parametros import novo_parser, parametros_de_argumentos, preparar_estado_inicial
from comum.saida import imprimir_cabecalho, imprimir_geracao, imprimir_grade, imprimir_resultado
from comum.visualizacao import Animacao
from distribuido import protocolo as p


def validar_workers(parametros, workers):
    """
    Recusa mais workers que linhas.

    Com uma faixa vazia, um worker ficaria entre dois vizinhos sem ter borda
    própria para repassar, e a cadeia de halos se quebraria.
    """
    parametros.validar()
    if not 1 <= workers <= parametros.linhas:
        raise ValueError(f"o número de workers ({workers}) precisa estar entre 1 e o número "
                         f"de linhas ({parametros.linhas})")


def executar_coordenador(parametros, servidor, workers, bits=False, mostrar=True,
                         mostrar_grade=False, ao_fim_da_geracao=None, verificar=False,
                         estatisticas=None, animacao=None, timeout=p.TIMEOUT_PADRAO):
    """
    Coordena uma execução com `workers` workers, usando o socket `servidor`.

    verificar=True faz os workers enviarem a faixa a cada geração, para o
    callback ao_fim_da_geracao receber a grade inteira (usado pelos testes).
    Devolve o mesmo dicionário de resultado das outras versões.
    """
    validar_workers(parametros, workers)
    linhas, colunas = parametros.linhas, parametros.colunas
    inicio_total = time.perf_counter()
    grade, limiares = preparar_estado_inicial(parametros)
    contagem = modelo.contar_faixa(grade, colunas, 1, linhas + 1)
    faixas = modelo.dividir_em_faixas(linhas, workers)
    # A grade inteira só é montada a cada geração quando alguém precisa dela.
    precisa_grade = verificar or animacao is not None or mostrar_grade

    if mostrar:
        imprimir_cabecalho("DISTRIBUÍDA", parametros, contagem,
                           [f"Workers: {workers} | Borda em bits: {'sim' if bits else 'não'}"])
    if animacao is not None:
        animacao.adicionar(0, grade)

    servidor.settimeout(timeout)
    conexoes = []
    try:
        # 1. Conexão dos workers; o rank é a ordem de chegada.
        enderecos = []
        for _ in range(workers):
            conexao, (host, _) = servidor.accept()
            p.configurar(conexao, timeout)
            _, ola = p.receber_json(conexao, p.OLA)
            conexoes.append(conexao)
            # O vizinho vai se conectar no IP de onde o worker veio, na porta que ele abriu.
            enderecos.append((host, ola["porta_halo"]))

        # 2. Distribuição das faixas (a grade foi gerada uma vez só, acima).
        for rank, (conexao, (ini, fim)) in enumerate(zip(conexoes, faixas)):
            p.enviar_json(conexao, p.INICIO, {
                "rank": rank, "workers": workers, "colunas": colunas, "inicio": ini, "fim": fim,
                "limiar": parametros.limiar, "geracoes": parametros.geracoes, "bits": bits,
                "resistencia": limiares is not None, "enviar_faixas": precisa_grade,
                "vizinho_abaixo": enderecos[rank + 1] if rank + 1 < workers else None,
            })
            # +1: a linha real r fica na linha r + 1 do vetor com moldura.
            p.enviar(conexao, p.GRADE, grade[(ini + 1) * colunas:(fim + 1) * colunas])
            if limiares is not None:
                p.enviar(conexao, p.LIMIARES, limiares[(ini + 1) * colunas:(fim + 1) * colunas])
        for conexao in conexoes:
            p.receber(conexao, p.PRONTO)
        for conexao in conexoes:
            p.enviar(conexao, p.LARGADA)

        # 3. Gerações: redução das contagens e decisão de parada.
        inicio = time.perf_counter()
        geracoes_executadas = 0
        for geracao in range(1, parametros.geracoes + 1):
            contagem = [0, 0, 0, 0]
            for rank, conexao in enumerate(conexoes):
                parcial = p.FORMATO_CONTAGEM.unpack(p.receber(conexao, p.CONTAGEM)[1])
                contagem = [a + b for a, b in zip(contagem, parcial)]
                if precisa_grade:
                    ini, fim = faixas[rank]
                    grade[(ini + 1) * colunas:(fim + 1) * colunas] = p.receber(conexao, p.FAIXA)[1]
            geracoes_executadas = geracao
            if mostrar:
                imprimir_geracao(geracao, contagem)
                if mostrar_grade:
                    imprimir_grade(grade, linhas, colunas)
            if estatisticas is not None:
                estatisticas.registrar_geracao(geracao, contagem)
            if animacao is not None:
                animacao.adicionar(geracao, grade)
            if ao_fim_da_geracao is not None:
                ao_fim_da_geracao(geracao, bytes(grade))
            vivo = contagem[modelo.ESPALHADOR] + contagem[modelo.BOT] > 0
            decisao = b"\x01" if vivo and geracao < parametros.geracoes else b"\x00"
            for conexao in conexoes:
                p.enviar(conexao, p.DECISAO, decisao)
            if not vivo:
                if mostrar:
                    print("\nA propagação terminou: não há mais espalhadores.")
                break
        tempo = time.perf_counter() - inicio

        # 4. Grade final e perfil de tempo de cada worker.
        perfis = []
        for conexao, (ini, fim) in zip(conexoes, faixas):
            grade[(ini + 1) * colunas:(fim + 1) * colunas] = p.receber(conexao, p.FAIXA)[1]
            perfis.append(p.receber_json(conexao, p.RESULTADO)[1])
    finally:
        for conexao in conexoes:
            conexao.close()
    tempo_total = time.perf_counter() - inicio_total

    if estatisticas is not None:
        estatisticas.tempo_laco = tempo
        estatisticas.tempo_total = tempo_total
        for perfil in perfis:
            estatisticas.registrar_trabalhador(perfil["rank"], perfil["calculo"],
                                               perfil["comunicacao"], perfil["espera"],
                                               perfil["bytes_enviados"])
    if mostrar:
        imprimir_resultado(tempo, contagem, linhas * colunas, tempo_total)
    return {"grade": bytes(grade), "contagem": contagem,
            "geracoes_executadas": geracoes_executadas, "tempo_laco": tempo,
            "tempo_total": tempo_total}


def adicionar_argumentos_distribuidos(parser):
    """Acrescenta os argumentos próprios da versão distribuída."""
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--bits", action="store_true",
                        help="melhoria: envia as bordas com 1 bit por célula")
    parser.add_argument("--timeout", type=float, default=p.TIMEOUT_PADRAO,
                        help="segundos máximos de espera por uma mensagem")
    return parser


def main(argv=None):
    """Lê os argumentos, espera os workers e coordena a execução."""
    parser = adicionar_argumentos_distribuidos(
        novo_parser("Coordenador da simulação distribuída de propagação de fake news"))
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço de escuta (0.0.0.0 para aceitar outras máquinas)")
    parser.add_argument("--porta", type=int, default=5000)
    args = parser.parse_args(argv)
    parametros = parametros_de_argumentos(args)
    validar_workers(parametros, args.workers)
    estatisticas = (Estatisticas("distribuida", parametros, args.workers)
                    if args.estatisticas else None)
    animacao = (Animacao(parametros.linhas, parametros.colunas, "distribuída")
                if args.animacao else None)
    servidor = p.criar_servidor(args.host, args.porta)
    print(f"Aguardando {args.workers} workers em {args.host}:{args.porta}...")
    try:
        executar_coordenador(parametros, servidor, args.workers, args.bits,
                             mostrar_grade=args.mostrar_grade, estatisticas=estatisticas,
                             animacao=animacao, timeout=args.timeout)
    finally:
        servidor.close()
    if estatisticas is not None:
        estatisticas.imprimir_resumo()
        print(f"Estatísticas gravadas em {estatisticas.salvar(args.estatisticas)}")
    if animacao is not None:
        print(f"Animação gravada em {animacao.salvar(args.animacao)}")


if __name__ == "__main__":
    main()
