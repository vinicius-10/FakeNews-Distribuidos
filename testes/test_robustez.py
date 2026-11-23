"""
Testes de robustez da versão distribuída (coordenador).

- Conexões que não são workers (um `Test-NetConnection`, um navegador, um
  scanner de portas) chegam antes dos workers: o coordenador descarta cada uma
  e a simulação continua com o mesmo resultado do professor.
- `tempo_total` mede só a execução: a espera até todos os workers conectarem
  (o tempo de alguém abrir os terminais) fica de fora.
- Um worker que cai ou trava vira erro com contexto (`ErroProtocolo` citando a
  geração), em vez de travar o coordenador.

Os workers rodam em threads (só usam sockets) e os que falham são falsos,
escritos em auxiliares.py; assim o teste controla a ordem de chegada.
"""

import socket
import threading
import time
import unittest

from comum.estatisticas import Estatisticas
from comum.parametros import ParametrosSimulacao
from distribuido import coordenador
from distribuido import protocolo as p

try:
    from .auxiliares import (Gravador, WorkerFalso, capturar_saida, conexoes_invalidas,
                             geracoes_do_professor, iniciar_workers_em_threads)
except ImportError:  # rodado com a pasta testes/ como raiz
    from auxiliares import (Gravador, WorkerFalso, capturar_saida, conexoes_invalidas,
                            geracoes_do_professor, iniciar_workers_em_threads)


class ComServidor(unittest.TestCase):
    """Abre o socket do coordenador numa porta livre de 127.0.0.1 e fecha no fim."""

    def setUp(self):
        self.servidor = p.criar_servidor("127.0.0.1", 0)
        self.porta = self.servidor.getsockname()[1]
        self.addCleanup(self.servidor.close)

    def par_de_sockets(self):
        """
        Dois sockets TCP conectados entre si (fechados no fim do teste).

        Não usa socket.socketpair(): no Linux ele cria um socket Unix, que não
        aceita TCP_NODELAY, e o coordenador só recebe conexões TCP.
        """
        self.servidor.settimeout(5)
        a = socket.create_connection(("127.0.0.1", self.porta), timeout=5)
        b, _ = self.servidor.accept()
        for sock in (a, b):
            sock.settimeout(5)
            self.addCleanup(sock.close)
        return a, b


class TestConexoesQueNaoSaoWorkers(ComServidor):

    def test_sao_descartadas_e_o_resultado_nao_muda(self):
        par = ParametrosSimulacao(linhas=15, colunas=12, geracoes=12,
                                  percentual_espalhadores=0.1, limiar=2)
        invalidas = conexoes_invalidas()
        # Todas chegam antes dos workers (o accept atende na ordem de chegada).
        abertas = [abrir(self.porta) for _, abrir in invalidas]
        for sock in abertas:
            if sock is not None:
                self.addCleanup(sock.close)
        threads = iniciar_workers_em_threads(self.porta, 3)

        gravador = Gravador(par.linhas, par.colunas)
        estatisticas = Estatisticas("teste", par, 3)
        texto, _ = capturar_saida(
            coordenador.executar_coordenador, par, self.servidor, 3, ao_fim_da_geracao=gravador,
            estatisticas=estatisticas, timeout=10, timeout_ola=0.5)
        for thread in threads:
            thread.join(10)

        self.assertEqual(gravador.grades, geracoes_do_professor(
            par.linhas, par.colunas, par.geracoes, par.percentual_espalhadores, par.limiar))
        # Os workers ficaram com os ranks 0..P-1: nenhuma conexão descartada gastou um rank.
        self.assertEqual(sorted(t["trabalhador"] for t in estatisticas.por_trabalhador),
                         [0, 1, 2])
        self.assertEqual(texto.count("descartada"), len(invalidas))
        self.assertIn("worker 3/3 conectado", texto)

    def test_ola_valido(self):
        a, b = self.par_de_sockets()
        p.enviar_json(a, p.OLA, {"porta_halo": 6000})
        self.assertEqual(coordenador._receber_ola(b, 1), 6000)

    def test_ola_invalido_vira_erro_de_protocolo(self):
        for ola in ({"porta_halo": 0}, {"porta_halo": 70000}, {"porta_halo": True},
                    {"porta_halo": 5000.5}, {"porta_halo": None}):
            with self.subTest(ola=ola):
                a, b = self.par_de_sockets()
                p.enviar_json(a, p.OLA, ola)
                with self.assertRaises(p.ErroProtocolo):
                    coordenador._receber_ola(b, 1)


class TestTempoTotal(ComServidor):

    def test_nao_conta_a_espera_pelos_workers(self):
        par = ParametrosSimulacao(linhas=10, colunas=10, geracoes=5, limiar=2)
        # Os workers só aparecem 1,5 s depois (como alguém abrindo os terminais).
        atraso = threading.Timer(1.5, iniciar_workers_em_threads, args=(self.porta, 2))
        atraso.start()
        self.addCleanup(atraso.cancel)
        inicio = time.perf_counter()
        texto, resultado = capturar_saida(coordenador.executar_coordenador, par,
                                          self.servidor, 2, timeout=10)
        self.assertGreaterEqual(time.perf_counter() - inicio, 1.5)  # a espera existiu
        self.assertLess(resultado["tempo_total"], 1.0)              # mas não foi contada
        self.assertGreaterEqual(resultado["tempo_total"], resultado["tempo_laco"])
        self.assertIn("Tempo desde a conexão de todos os workers", texto)


class TestWorkerQueFalha(ComServidor):

    PAR = ParametrosSimulacao(linhas=6, colunas=6, geracoes=5, percentual_espalhadores=0.3,
                              limiar=2)

    def test_worker_que_cai_vira_erro_com_a_geracao(self):
        falso = WorkerFalso(self.porta, "fechar")
        falso.start()
        inicio = time.monotonic()
        with self.assertRaises(p.ErroProtocolo) as erro:
            coordenador.executar_coordenador(self.PAR, self.servidor, 1, mostrar=False,
                                             timeout=30)
        self.assertLess(time.monotonic() - inicio, 5)
        self.assertIn("geração 1", str(erro.exception))
        # No Windows a queda pode chegar como reset; os dois são ConnectionError.
        self.assertIsInstance(erro.exception.__cause__, ConnectionError)
        falso.join(5)
        self.assertIsNone(falso.erro)

    def test_worker_mudo_vira_erro_por_timeout(self):
        falso = WorkerFalso(self.porta, "calar")
        falso.start()
        self.addCleanup(falso.parar)
        inicio = time.monotonic()
        with self.assertRaises(p.ErroProtocolo) as erro:
            coordenador.executar_coordenador(self.PAR, self.servidor, 1, mostrar=False,
                                             timeout=1)
        self.assertLess(time.monotonic() - inicio, 5)
        self.assertIn("geração 1", str(erro.exception))
        self.assertIsInstance(erro.exception.__cause__, TimeoutError)
        falso.parar()
        falso.join(5)
        self.assertIsNone(falso.erro)


if __name__ == "__main__":
    unittest.main()
