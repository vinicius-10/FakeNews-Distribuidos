"""
Protocolo de mensagens da versão distribuída (sockets TCP).

Formato de toda mensagem
------------------------
    +------+---------------------+-----------------+
    | tipo | tamanho da carga    | carga           |
    | 1 B  | 4 B (big-endian)    | `tamanho` bytes |
    +------+---------------------+-----------------+

O TCP entrega um fluxo de bytes, não mensagens: um recv pode devolver só um
pedaço do que foi enviado, ou o fim de uma mensagem junto com o começo da
próxima. Por isso o tamanho vai no cabeçalho e a leitura repete recv até
completar exatamente esse número de bytes.

Mensagens (quem envia → quem recebe)
-----------------------------------
OLA        worker → coordenador   JSON {"porta_halo"}: porta em que o worker espera o vizinho de cima
INICIO     coordenador → worker   JSON com a faixa, os parâmetros e o endereço do vizinho de baixo
GRADE      coordenador → worker   bytes das linhas da faixa (estado inicial)
LIMIARES   coordenador → worker   bytes dos limiares individuais da faixa (melhoria resistência)
PRONTO     worker → coordenador   vazio: já está conectado aos vizinhos
LARGADA    coordenador → worker   vazio: todos prontos, começa a geração 1
HALO       worker ↔ worker        uma linha de borda (1 byte ou 1 bit por célula)
CONTAGEM   worker → coordenador   4 inteiros: ignorantes, espalhadores, inativos, bots da faixa
FAIXA      worker → coordenador   bytes das linhas da faixa (verificação, animação e resultado final)
DECISAO    coordenador → worker   1 byte: 1 = continua, 0 = para
RESULTADO  worker → coordenador   JSON com o perfil de tempo do worker
"""

import json
import socket
import struct
import time

OLA, INICIO, GRADE, LIMIARES, PRONTO, LARGADA, HALO, CONTAGEM, FAIXA, DECISAO, RESULTADO = range(1, 12)

NOMES = {OLA: "OLA", INICIO: "INICIO", GRADE: "GRADE", LIMIARES: "LIMIARES", PRONTO: "PRONTO",
         LARGADA: "LARGADA", HALO: "HALO", CONTAGEM: "CONTAGEM", FAIXA: "FAIXA",
         DECISAO: "DECISAO", RESULTADO: "RESULTADO"}

CABECALHO = struct.Struct("!BI")    # tipo (1 byte) + tamanho (4 bytes)
FORMATO_CONTAGEM = struct.Struct("!4Q")  # 4 inteiros sem sinal de 8 bytes

TIMEOUT_PADRAO = 600  # segundos; toda espera tem limite para virar erro, não travar


class ErroProtocolo(Exception):
    """Mensagem inesperada (tipo errado ou conteúdo inválido)."""


def enviar(sock, tipo, carga=b""):
    """Envia uma mensagem; sendall repete o envio até mandar todos os bytes."""
    sock.sendall(CABECALHO.pack(tipo, len(carga)) + bytes(carga))
    return CABECALHO.size + len(carga)


def _receber_exato(sock, quantidade):
    """Lê exatamente `quantidade` bytes, juntando quantos recv forem necessários."""
    dados = bytearray(quantidade)
    view = memoryview(dados)
    recebidos = 0
    while recebidos < quantidade:
        n = sock.recv_into(view[recebidos:])
        if n == 0:
            raise ConnectionError("conexão fechada no meio de uma mensagem")
        recebidos += n
    return bytes(dados)


def receber(sock, esperado=None):
    """
    Recebe uma mensagem inteira e devolve (tipo, carga).

    Se `esperado` for dado, uma mensagem de outro tipo é erro de protocolo
    (por exemplo, um worker fora de sincronia com os outros).
    """
    tipo, tamanho = CABECALHO.unpack(_receber_exato(sock, CABECALHO.size))
    carga = _receber_exato(sock, tamanho) if tamanho else b""
    if esperado is not None and tipo != esperado:
        raise ErroProtocolo(f"esperava {NOMES.get(esperado, esperado)}, "
                            f"chegou {NOMES.get(tipo, tipo)}")
    return tipo, carga


def enviar_json(sock, tipo, dados):
    """Envia um dicionário como JSON em UTF-8."""
    return enviar(sock, tipo, json.dumps(dados).encode("utf-8"))


def receber_json(sock, esperado=None):
    """Recebe uma mensagem JSON e devolve (tipo, dicionário)."""
    tipo, carga = receber(sock, esperado)
    return tipo, json.loads(carga.decode("utf-8"))


def configurar(sock, timeout):
    """
    Ajusta um socket conectado: timeout e TCP_NODELAY.

    TCP_NODELAY desliga o algoritmo de Nagle, que seguraria as mensagens
    pequenas (bordas, contagens) esperando juntar mais dados e somaria latência
    a cada geração.
    """
    sock.settimeout(timeout)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sock


def criar_servidor(host, porta, fila=64):
    """
    Abre um socket escutando em host:porta (porta 0 = o sistema escolhe uma livre).

    Não usa SO_REUSEADDR (nem socket.create_server, que o liga no Linux): no
    Windows essa opção deixa outro processo usar a mesma porta.
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen(fila)
    return servidor


def conectar(host, porta, timeout, espera_maxima=30.0):
    """
    Conecta a host:porta, tentando de novo por até `espera_maxima` segundos.

    Num teste entre máquinas os workers podem ser iniciados antes do
    coordenador; as novas tentativas evitam ter que acertar a ordem na mão.
    """
    limite = time.monotonic() + espera_maxima
    while True:
        try:
            return configurar(socket.create_connection((host, porta), timeout=timeout), timeout)
        except (ConnectionRefusedError, socket.timeout, OSError):
            if time.monotonic() >= limite:
                raise
            time.sleep(0.2)
