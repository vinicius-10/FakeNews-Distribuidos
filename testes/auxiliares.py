"""
Funções de apoio dos testes: referência do professor, comparação de grades,
captura do que é impresso e workers (reais e falsos) para a versão distribuída.

A referência de comportamento é o código sequencial do professor
(sequencial/fakenews_sequencial_original.py), usado aqui sem nenhuma alteração.
"""

import contextlib
import io
import socket
import threading

from sequencial import fakenews_sequencial_original as professor


def capturar_saida(funcao, *args, **kwargs):
    """Executa funcao(*args, **kwargs) e devolve (texto impresso, valor devolvido)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        resultado = funcao(*args, **kwargs)
    return buffer.getvalue(), resultado


def geracoes_do_professor(linhas, colunas, geracoes, percentual, limiar, semente=42):
    """
    Executa o laço da versão do professor e devolve a grade de cada geração.

    Repete a lógica de executar_simulacao (que só imprime) para guardar as
    grades: mesma grade inicial, mesma transição e mesma parada antecipada.
    """
    grade = professor.criar_grade(linhas, colunas, percentual, semente)
    grades = []
    for _ in range(geracoes):
        grade = professor.proxima_geracao(grade, limiar)
        grades.append(grade)
        if professor.contar_estados(grade)[professor.ESPALHADOR] == 0:
            break
    return grades


class Gravador:
    """Guarda a grade de cada geração recebida pelo callback ao_fim_da_geracao."""

    def __init__(self, linhas, colunas):
        self.linhas = linhas
        self.colunas = colunas
        self.grades = []

    def __call__(self, geracao, grade_plana):
        # Importado aqui para que os testes do modelo possam falhar sozinhos.
        from comum.modelo import plana_para_lista
        assert geracao == len(self.grades) + 1, "gerações fora de ordem"
        self.grades.append(plana_para_lista(grade_plana, self.linhas, self.colunas))


# ---------------------------------------------------------------------------
# Versão distribuída: workers em threads, workers falsos e conexões inválidas
# ---------------------------------------------------------------------------

def iniciar_workers_em_threads(porta, quantidade, timeout=10):
    """
    Sobe `quantidade` workers reais em threads, conectando em 127.0.0.1:porta.

    O worker só usa sockets, então roda igual numa thread; assim o teste
    controla quando cada um conecta, sem o custo de criar processos.
    """
    from distribuido import worker
    threads = [threading.Thread(target=worker.executar_worker,
                                args=("127.0.0.1", porta, "127.0.0.1", timeout),
                                name=f"worker-teste-{i}", daemon=True)
               for i in range(quantidade)]
    for thread in threads:
        thread.start()
    return threads


def _enviar_bruto(dados):
    """Fábrica de conexão inválida: envia `dados` e fecha."""
    def abrir(porta):
        sock = socket.create_connection(("127.0.0.1", porta), timeout=5)
        sock.sendall(dados)
        sock.close()
        return None
    return abrir


def _conectar_e_fechar(porta):
    socket.create_connection(("127.0.0.1", porta), timeout=5).close()
    return None


def _conectar_e_calar(porta):
    """Conecta e não envia nada; devolve o socket para o teste fechar no fim."""
    return socket.create_connection(("127.0.0.1", porta), timeout=5)


def _mensagem(tipo, carga):
    from distribuido import protocolo as p
    return p.CABECALHO.pack(tipo, len(carga)) + carga


def conexoes_invalidas():
    """
    Conexões que chegam na porta do coordenador e não são workers.

    Cada item é (nome, função(porta) -> socket aberto ou None). As que ficam
    abertas (a silenciosa) são devolvidas para o teste fechar depois.
    """
    from distribuido import protocolo as p
    return [
        ("conecta e fecha", _conectar_e_fechar),
        ("HTTP", _enviar_bruto(b"GET / HTTP/1.1\r\nHost: coordenador\r\n\r\n")),
        ("tipo errado", _enviar_bruto(_mensagem(p.PRONTO, b""))),
        ("JSON inválido", _enviar_bruto(_mensagem(p.OLA, b"{porta_halo: 5"))),
        ("UTF-8 inválido", _enviar_bruto(_mensagem(p.OLA, b"\xff\xfe"))),
        ("sem porta_halo", _enviar_bruto(_mensagem(p.OLA, b'{"porta": 5000}'))),
        ("porta_halo inválida", _enviar_bruto(_mensagem(p.OLA, b'{"porta_halo": "5000"}'))),
        ("JSON que não é objeto", _enviar_bruto(_mensagem(p.OLA, b"[5000]"))),
        ("silenciosa", _conectar_e_calar),
    ]


class WorkerFalso(threading.Thread):
    """
    Worker que segue o protocolo até receber a LARGADA e então falha.

    comportamento="fechar": fecha a conexão (como um worker que caiu);
    comportamento="calar": fica com a conexão aberta sem responder, até
    `parar()` (como um worker travado). Só serve para 1 worker, que não tem
    vizinhos.
    """

    def __init__(self, porta, comportamento):
        super().__init__(name=f"worker-falso-{comportamento}", daemon=True)
        self.porta = porta
        self.comportamento = comportamento
        self._parar = threading.Event()
        self.erro = None

    def run(self):
        from distribuido import protocolo as p
        try:
            with socket.create_connection(("127.0.0.1", self.porta), timeout=10) as sock:
                p.enviar_json(sock, p.OLA, {"porta_halo": 1})
                p.receber_json(sock, p.INICIO)
                p.receber(sock, p.GRADE)
                p.enviar(sock, p.PRONTO)
                p.receber(sock, p.LARGADA)
                if self.comportamento == "calar":
                    self._parar.wait(10)
        except Exception as erro:  # guardado para o teste conferir
            self.erro = erro

    def parar(self):
        self._parar.set()
