"""
Worker da versão distribuída.

Cada worker guarda só a sua faixa de linhas, com duas linhas a mais (o halo):
a de cima recebe a última linha do vizinho de cima e a de baixo recebe a
primeira linha do vizinho de baixo. Na borda da grade o halo fica com zeros,
que é a borda fixa do professor. A cada geração:

1. troca as bordas com os vizinhos (halo);
2. calcula a sua faixa com o núcleo comum;
3. envia ao coordenador a contagem de estados da faixa;
4. espera a decisão do coordenador (continuar ou parar).

O passo 4 funciona como a barreira da versão paralela: ninguém começa a
geração seguinte antes de todos terminarem a atual.

Topologia: os workers formam uma cadeia (0, 1, ..., P-1, de cima para baixo).
O worker k se conecta ao k+1 (vizinho de baixo) e aceita a conexão do k-1
(vizinho de cima). As bordas vão direto de worker para worker, sem passar pelo
coordenador.

Uso: python -m distribuido.worker --coordenador 192.168.0.10:5000 --escutar 0.0.0.0
"""

import argparse
import time

from comum import modelo
from distribuido import protocolo as p


def trocar_bordas(atual, colunas, altura, acima, abaixo, rank, bits):
    """
    Troca as linhas de borda com os vizinhos e grava o que chega no halo.

    Ordem par/ímpar para não haver deadlock: worker par envia e depois recebe,
    worker ímpar recebe e depois envia. Assim, em cada par de vizinhos, um
    lado sempre está lendo enquanto o outro escreve, independentemente do
    tamanho do buffer do socket (que, se lotasse, travaria dois envios
    simultâneos). Devolve o número de bytes enviados.
    """
    primeira = colunas            # início da primeira linha real da faixa
    ultima = altura * colunas     # início da última linha real da faixa
    halo_cima = 0
    halo_baixo = (altura + 1) * colunas

    def codificar(inicio):
        if bits:
            return modelo.empacotar_bits(atual, inicio, colunas)
        return bytes(atual[inicio:inicio + colunas])

    def gravar(dados, inicio):
        if bits:
            modelo.desempacotar_bits(dados, atual, inicio, colunas)
        else:
            atual[inicio:inicio + colunas] = dados

    enviados = 0

    def enviar_para(vizinho, inicio):
        nonlocal enviados
        if vizinho is not None:
            enviados += p.enviar(vizinho, p.HALO, codificar(inicio))

    def receber_de(vizinho, inicio):
        if vizinho is not None:
            gravar(p.receber(vizinho, p.HALO)[1], inicio)

    if rank % 2 == 0:
        enviar_para(abaixo, ultima)
        receber_de(abaixo, halo_baixo)
        enviar_para(acima, primeira)
        receber_de(acima, halo_cima)
    else:
        receber_de(acima, halo_cima)
        enviar_para(acima, primeira)
        receber_de(abaixo, halo_baixo)
        enviar_para(abaixo, ultima)
    return enviados


def executar_worker(host_coordenador, porta_coordenador, escutar="127.0.0.1",
                    timeout=p.TIMEOUT_PADRAO):
    """Conecta ao coordenador, recebe a faixa e executa as gerações."""
    # A porta de escuta (para o vizinho de cima) é aberta antes de falar com o
    # coordenador; porta 0 deixa o sistema escolher uma livre.
    ouvinte = p.criar_servidor(escutar, 0, fila=1)
    ouvinte.settimeout(timeout)
    coordenador = None
    acima = abaixo = None
    try:
        coordenador = p.conectar(host_coordenador, porta_coordenador, timeout)
        p.enviar_json(coordenador, p.OLA, {"porta_halo": ouvinte.getsockname()[1]})
        _, cfg = p.receber_json(coordenador, p.INICIO)
        rank, colunas = cfg["rank"], cfg["colunas"]
        altura = cfg["fim"] - cfg["inicio"]
        moldura = bytes(colunas)

        # Faixa local com halo: linha 0 e linha altura+1 são as bordas dos vizinhos.
        atual = bytearray(moldura + p.receber(coordenador, p.GRADE)[1] + moldura)
        nova = bytearray(len(atual))
        limiares = None
        if cfg["resistencia"]:
            limiares = bytearray(moldura + p.receber(coordenador, p.LIMIARES)[1] + moldura)

        # Conectar-se ao vizinho de baixo antes de aceitar o de cima não trava:
        # o connect termina assim que o ouvinte do vizinho está escutando,
        # mesmo que ele ainda não tenha chamado accept.
        if cfg["vizinho_abaixo"] is not None:
            abaixo = p.conectar(cfg["vizinho_abaixo"][0], cfg["vizinho_abaixo"][1], timeout)
        if rank > 0:
            acima = p.configurar(ouvinte.accept()[0], timeout)
        ouvinte.close()
        p.enviar(coordenador, p.PRONTO)
        p.receber(coordenador, p.LARGADA)

        calculo = comunicacao = espera = 0.0
        bytes_enviados = 0
        for _ in range(cfg["geracoes"]):
            t0 = time.perf_counter()
            bytes_enviados += trocar_bordas(atual, colunas, altura, acima, abaixo, rank,
                                            cfg["bits"])
            t1 = time.perf_counter()
            modelo.calcular_faixa(atual, nova, colunas, 1, altura + 1, cfg["limiar"], limiares)
            contagem = modelo.contar_faixa(nova, colunas, 1, altura + 1)
            t2 = time.perf_counter()
            bytes_enviados += p.enviar(coordenador, p.CONTAGEM,
                                       p.FORMATO_CONTAGEM.pack(*contagem))
            if cfg["enviar_faixas"]:
                bytes_enviados += p.enviar(coordenador, p.FAIXA,
                                           nova[colunas:(altura + 1) * colunas])
            t3 = time.perf_counter()
            continuar = p.receber(coordenador, p.DECISAO)[1] == b"\x01"
            t4 = time.perf_counter()
            comunicacao += (t1 - t0) + (t3 - t2)
            calculo += t2 - t1
            espera += t4 - t3
            # Troca de buffers: só referências, sem cópia.
            atual, nova = nova, atual
            if not continuar:
                break

        p.enviar(coordenador, p.FAIXA, atual[colunas:(altura + 1) * colunas])
        p.enviar_json(coordenador, p.RESULTADO, {
            "rank": rank, "calculo": calculo, "comunicacao": comunicacao,
            "espera": espera, "bytes_enviados": bytes_enviados})
    finally:
        for sock in (acima, abaixo, coordenador, ouvinte):
            if sock is not None:
                sock.close()


def main(argv=None):
    """Lê os argumentos e executa o worker."""
    parser = argparse.ArgumentParser(description="Worker da simulação distribuída")
    parser.add_argument("--coordenador", default="127.0.0.1:5000", metavar="HOST:PORTA")
    parser.add_argument("--escutar", default="127.0.0.1",
                        help="endereço para o vizinho se conectar (0.0.0.0 entre máquinas)")
    parser.add_argument("--timeout", type=float, default=p.TIMEOUT_PADRAO)
    args = parser.parse_args(argv)
    host, _, porta = args.coordenador.rpartition(":")
    executar_worker(host, int(porta), args.escutar, args.timeout)


if __name__ == "__main__":
    main()
