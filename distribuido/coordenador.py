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

from contextlib import contextmanager
import struct
import time

from comum import modelo
from comum.estatisticas import Estatisticas
from comum.parametros import novo_parser, parametros_de_argumentos, preparar_estado_inicial
from comum.saida import imprimir_cabecalho, imprimir_geracao, imprimir_grade, imprimir_resultado
from comum.visualizacao import Animacao
from distribuido import protocolo as p


@contextmanager
def _contexto(operacao, **detalhes):
    """Envolve uma operação e, se falhar, adiciona contexto à mensagem de erro."""
    try:
        yield
    except (ConnectionError, p.ErroProtocolo, OSError, ValueError, struct.error) as erro:
        partes = [f"durante {operacao}"]
        for k, v in detalhes.items():
            partes.append(f"{k}={v}")
        contexto = " (" + ", ".join(partes) + ")"
        raise p.ErroProtocolo(
            f"{type(erro).__name__} {contexto}: {erro}") from erro


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


def _receber_ola(conexao, timeout_ola):
    """
    Lê o OLA de uma conexão recém-aceita e devolve a `porta_halo` do worker.

    Qualquer outra coisa (conexão fechada, silêncio além de `timeout_ola`, tipo
    de mensagem errado, JSON ou UTF-8 inválido, porta ausente ou fora de
    1..65535) vira ErroProtocolo: quem chamou descarta a conexão, porque ela
    não é de um worker (ex.: Test-NetConnection, navegador, scanner de portas).
    """
    try:
        p.configurar(conexao, timeout_ola)
        _, ola = p.receber_json(conexao, p.OLA)
    # json.JSONDecodeError e UnicodeDecodeError são ValueError; o timeout do
    # socket (TimeoutError) e as falhas de conexão são OSError.
    except (OSError, ValueError, struct.error, p.ErroProtocolo) as erro:
        raise p.ErroProtocolo(f"{type(erro).__name__}: {erro}") from erro
    porta = ola.get("porta_halo") if isinstance(ola, dict) else None
    # bool é subclasse de int em Python: True não pode passar por porta 1.
    if isinstance(porta, bool) or not isinstance(porta, int) or not 1 <= porta <= 65535:
        raise p.ErroProtocolo(f"OLA sem porta_halo válida: {ola!r}"[:200])
    return porta


def executar_coordenador(parametros, servidor, workers, bits=False, mostrar=True,
                         mostrar_grade=False, ao_fim_da_geracao=None, verificar=False,
                         estatisticas=None, animacao=None, timeout=p.TIMEOUT_PADRAO,
                         timeout_ola=p.TIMEOUT_OLA):
    """
    Coordena uma execução com `workers` workers, usando o socket `servidor`.

    verificar=True faz os workers enviarem a faixa a cada geração, para o
    callback ao_fim_da_geracao receber a grade inteira (usado pelos testes).
    Devolve o mesmo dicionário de resultado das outras versões.

    `tempo_total` mede só a execução: começa depois que o último worker
    conecta (entre máquinas, a espera é o tempo de alguém abrir os terminais,
    não custo do programa) e vai até a coleta do resultado.
    """
    validar_workers(parametros, workers)
    linhas, colunas = parametros.linhas, parametros.colunas
    grade, limiares = preparar_estado_inicial(parametros)
    contagem = modelo.contar_faixa(grade, colunas, 1, linhas + 1)
    faixas = modelo.dividir_em_faixas(linhas, workers)
    # A grade inteira só é montada a cada geração quando alguém precisa dela.
    # `ao_fim_da_geracao` também precisa: sem isso o callback receberia sempre a
    # grade inicial (as faixas nunca chegam do worker) e o erro seria silencioso.
    precisa_grade = (verificar or ao_fim_da_geracao is not None
                     or animacao is not None or mostrar_grade)

    if mostrar:
        imprimir_cabecalho("DISTRIBUÍDA", parametros, contagem,
                           [f"Workers: {workers} | Borda em bits: {'sim' if bits else 'não'}"])
    if animacao is not None:
        animacao.adicionar(0, grade)

    servidor.settimeout(timeout)
    conexoes = []
    perfis = []
    if mostrar:
        print(f"Aguardando {workers} worker(s); cada um é avisado assim que conecta...")
    try:
        # 1. Conexão dos workers; o rank é a ordem de chegada. Uma conexão que
        #    não manda um OLA válido é fechada e não gasta um rank.
        enderecos = []
        while len(conexoes) < workers:
            rank = len(conexoes)
            with _contexto(f"aceitar conexão do worker {rank}"):
                conexao, (host, porta_origem) = servidor.accept()
            try:
                porta_halo = _receber_ola(conexao, min(timeout_ola, timeout))
            except p.ErroProtocolo as erro:
                conexao.close()
                if mostrar:
                    print(f"  conexão de {host}:{porta_origem} descartada "
                          f"(não é um worker: {erro})", flush=True)
                continue
            p.configurar(conexao, timeout)
            conexoes.append(conexao)
            # O vizinho vai se conectar no IP de onde o worker veio, na porta que ele abriu.
            enderecos.append((host, porta_halo))
            # `accept` espera até o timeout (600 s por padrão); avisar a cada
            # conexão evita a impressão de programa travado quando falta subir
            # um dos workers.
            if mostrar:
                print(f"  worker {rank + 1}/{workers} conectado", flush=True)

        # Todos conectados: só agora o relógio do tempo total começa.
        inicio_total = time.perf_counter()

        # 2. Distribuição das faixas (a grade foi gerada uma vez só, acima).
        for rank, (conexao, (ini, fim)) in enumerate(zip(conexoes, faixas)):
            with _contexto(f"distribuir faixa para o worker {rank}", faixa=f"{ini}..{fim}"):
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
        for rank, conexao in enumerate(conexoes):
            with _contexto(f"aguardar PRONTO do worker {rank}"):
                p.receber(conexao, p.PRONTO)
        for rank, conexao in enumerate(conexoes):
            with _contexto(f"enviar LARGADA para o worker {rank}"):
                p.enviar(conexao, p.LARGADA)

        # 3. Gerações: redução das contagens e decisão de parada.
        inicio = time.perf_counter()
        geracoes_executadas = 0
        for geracao in range(1, parametros.geracoes + 1):
            contagem = [0, 0, 0, 0]
            for rank, conexao in enumerate(conexoes):
                ini, fim = faixas[rank]
                with _contexto(f"receber CONTAGEM do worker {rank} na geração {geracao}",
                               faixa=f"{ini}..{fim}"):
                    parcial = p.FORMATO_CONTAGEM.unpack(p.receber(conexao, p.CONTAGEM)[1])
                    contagem = [a + b for a, b in zip(contagem, parcial)]
                if precisa_grade:
                    with _contexto(f"receber FAIXA do worker {rank} na geração {geracao}", faixa=f"{ini}..{fim}"):
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
            for rank, conexao in enumerate(conexoes):
                with _contexto(f"enviar DECISAO ao worker {rank} na geração {geracao}"):
                    p.enviar(conexao, p.DECISAO, decisao)
            if not vivo:
                if mostrar:
                    print("\nA propagação terminou: não há mais espalhadores.")
                break
        tempo = time.perf_counter() - inicio

        # 4. Grade final e perfil de tempo de cada worker.
        for rank, (conexao, (ini, fim)) in enumerate(zip(conexoes, faixas)):
            with _contexto(f"receber FAIXA final do worker {rank}", faixa=f"{ini}..{fim}"):
                grade[(ini + 1) * colunas:(fim + 1) * colunas] = p.receber(conexao, p.FAIXA)[1]
            with _contexto(f"receber RESULTADO do worker {rank}"):
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
        imprimir_resultado(tempo, contagem, linhas * colunas, tempo_total,
                           "Tempo desde a conexão de todos os workers")
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
