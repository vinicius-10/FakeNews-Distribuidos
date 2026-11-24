"""
Testes da medição em rede real (várias máquinas).

- Ordem fixa das faixas: o worker pode mandar `ordem` no OLA e o coordenador
  distribui as faixas por essa ordem, não pela ordem de chegada. Sem isso, numa
  bateria com repetições a máquina que fica com a faixa do meio (dois vizinhos)
  mudaria de uma execução para outra.
- Agente e bateria (`distribuido/agente.py` e `experimentos/medir_rede.py`): a
  bateria inteira roda com dois agentes em 127.0.0.1 e todas as linhas do CSV
  conferem com a sequencial.

Os workers da ordem rodam em threads (só usam sockets), para o teste controlar
a ordem de chegada.
"""

import csv
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from comum.parametros import ParametrosSimulacao
from distribuido import coordenador
from distribuido import protocolo as p
from distribuido import worker

try:
    from .auxiliares import capturar_saida, geracoes_do_professor, Gravador
except ImportError:  # rodado com a pasta testes/ como raiz
    from auxiliares import capturar_saida, geracoes_do_professor, Gravador

RAIZ = Path(__file__).resolve().parent.parent


def subir_worker_com_ordem(porta, ordem, retornos):
    """Sobe um worker real numa thread e guarda (ordem, retorno) quando ele termina."""
    def alvo():
        retornos.append((ordem, worker.executar_worker("127.0.0.1", porta, "127.0.0.1", 10,
                                                       ordem=ordem)))
    thread = threading.Thread(target=alvo, name=f"worker-ordem-{ordem}", daemon=True)
    thread.start()
    return thread


class TestOrdemFixa(unittest.TestCase):

    def setUp(self):
        self.servidor = p.criar_servidor("127.0.0.1", 0)
        self.porta = self.servidor.getsockname()[1]
        self.addCleanup(self.servidor.close)
        self.par = ParametrosSimulacao(linhas=15, colunas=12, geracoes=10,
                                       percentual_espalhadores=0.1, limiar=2)

    def rodar(self, ordens):
        """Conecta os workers na ordem da lista (um de cada vez) e roda o coordenador."""
        retornos = []
        threads = []
        resultado = {}

        def coordenar():
            gravador = Gravador(self.par.linhas, self.par.colunas)
            resultado["texto"], _ = capturar_saida(
                coordenador.executar_coordenador, self.par, self.servidor, len(ordens),
                ao_fim_da_geracao=gravador, timeout=10)
            resultado["grades"] = gravador.grades

        thread_coord = threading.Thread(target=coordenar, daemon=True)
        thread_coord.start()
        for ordem in ordens:
            threads.append(subir_worker_com_ordem(self.porta, ordem, retornos))
            time.sleep(0.15)  # garante a ordem de chegada
        thread_coord.join(30)
        for thread in threads:
            thread.join(10)
        self.assertFalse(thread_coord.is_alive(), "coordenador não terminou")
        return resultado, dict(retornos)

    def test_faixas_seguem_a_ordem_e_nao_a_chegada(self):
        # Chegam 2, 0, 1: os ranks têm de ser 2, 0, 1 mesmo assim.
        resultado, retornos = self.rodar([2, 0, 1])
        self.assertEqual({ordem: r["rank"] for ordem, r in retornos.items()},
                         {0: 0, 1: 1, 2: 2})
        # E a faixa de cada rank é a de cima para baixo: 0..5, 5..10, 10..15.
        self.assertEqual([(retornos[o]["inicio"], retornos[o]["fim"]) for o in range(3)],
                         [(0, 5), (5, 10), (10, 15)])
        self.assertEqual(resultado["grades"], geracoes_do_professor(
            self.par.linhas, self.par.colunas, self.par.geracoes,
            self.par.percentual_espalhadores, self.par.limiar))

    def test_sem_ordem_vale_a_chegada(self):
        retornos = []
        threads = []
        thread_coord = threading.Thread(
            target=capturar_saida, daemon=True,
            args=(coordenador.executar_coordenador, self.par, self.servidor, 2),
            kwargs={"timeout": 10})
        thread_coord.start()
        for i in range(2):
            def alvo(i=i):
                retornos.append((i, worker.executar_worker("127.0.0.1", self.porta,
                                                           "127.0.0.1", 10)))
            threads.append(threading.Thread(target=alvo, daemon=True))
            threads[-1].start()
            time.sleep(0.15)
        thread_coord.join(30)
        for thread in threads:
            thread.join(10)
        self.assertEqual({i: r["rank"] for i, r in retornos}, {0: 0, 1: 1})


class TestOlaComOrdem(unittest.TestCase):

    def setUp(self):
        self.servidor = p.criar_servidor("127.0.0.1", 0)
        self.porta = self.servidor.getsockname()[1]
        self.addCleanup(self.servidor.close)
        self.servidor.settimeout(5)

    def par(self):
        a = __import__("socket").create_connection(("127.0.0.1", self.porta), timeout=5)
        b, _ = self.servidor.accept()
        for sock in (a, b):
            sock.settimeout(5)
            self.addCleanup(sock.close)
        return a, b

    def test_ordem_valida(self):
        a, b = self.par()
        p.enviar_json(a, p.OLA, {"porta_halo": 6000, "ordem": 3})
        self.assertEqual(coordenador._ler_ola(b, 1), (6000, 3))

    def test_sem_ordem(self):
        a, b = self.par()
        p.enviar_json(a, p.OLA, {"porta_halo": 6000})
        self.assertEqual(coordenador._ler_ola(b, 1), (6000, None))

    def test_ordem_invalida_descarta(self):
        for ordem in (-1, "2", 1.5, True, [0]):
            with self.subTest(ordem=ordem):
                a, b = self.par()
                p.enviar_json(a, p.OLA, {"porta_halo": 6000, "ordem": ordem})
                with self.assertRaises(p.ErroProtocolo):
                    coordenador._ler_ola(b, 1)


class TestBateriaEmLocalhost(unittest.TestCase):
    """A bateria inteira (3 fases) com 2 agentes em subprocessos, perfil de fumaça."""

    def test_bateria_completa_confere_com_a_sequencial(self):
        from experimentos import medir_rede

        with tempfile.TemporaryDirectory() as pasta:
            servidor = p.criar_servidor("127.0.0.1", 0)
            porta = servidor.getsockname()[1]
            agentes = [subprocess.Popen(
                [sys.executable, "-m", "distribuido.agente",
                 "--coordenador", f"127.0.0.1:{porta}", "--escutar", "127.0.0.1",
                 "--posicao", str(i), "--nome", f"agente-{i}"],
                cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                for i in (1, 0)]  # chegam fora de ordem de propósito
            try:
                texto, _ = capturar_saida(
                    medir_rede.executar_bateria, servidor, maquinas=2, perfil="fumaca",
                    pasta=Path(pasta), rede="loopback (teste)", timeout=60)
            finally:
                servidor.close()
                codigos = []
                for agente in agentes:
                    try:
                        _, erro = agente.communicate(timeout=30)
                    except subprocess.TimeoutExpired:
                        agente.kill()
                        _, erro = agente.communicate()
                    codigos.append((agente.returncode, erro.decode("utf-8", "replace")))
            for codigo, erro in codigos:
                self.assertEqual(codigo, 0, erro)

            with open(Path(pasta) / "sequencial_maquinas.csv", encoding="utf-8") as arq:
                fase1 = list(csv.DictReader(arq))
            with open(Path(pasta) / "medicoes.csv", encoding="utf-8") as arq:
                rede = list(csv.DictReader(arq))
            with open(Path(pasta) / "ambiente_maquinas.csv", encoding="utf-8") as arq:
                ambiente = list(csv.DictReader(arq))

        # Fase 1: as duas máquinas, mesmo hash em cada tamanho.
        self.assertEqual({l["maquina"] for l in fase1}, {"agente-0", "agente-1"})
        por_tamanho = {}
        for linha in fase1:
            por_tamanho.setdefault(linha["linhas"], set()).add(linha["hash_grade"])
        self.assertTrue(all(len(h) == 1 for h in por_tamanho.values()), por_tamanho)
        # Ambiente das duas, na ordem da posição.
        self.assertEqual([a["maquina"] for a in ambiente], ["agente-0", "agente-1"])

        # Fases 2 e 3: tudo confere com a sequencial.
        self.assertTrue(rede)
        self.assertEqual({l["confere"] for l in rede}, {"sim"}, texto)
        self.assertEqual({l["fase"] for l in rede}, {"2", "3"})
        self.assertEqual({int(l["hosts"]) for l in rede}, {1, 2})
        for linha in rede:
            self.assertEqual(int(linha["workers"]),
                             int(linha["hosts"]) * int(linha["workers_por_host"]))
            self.assertEqual(linha["maquinas"],
                             "agente-0" if linha["hosts"] == "1" else "agente-0;agente-1")
        self.assertIn("distribuida_rede_bits", {l["versao"] for l in rede})

    def test_retomada_pula_o_que_ja_foi_medido(self):
        from experimentos import medir_rede

        plano = medir_rede.montar_plano("fumaca", 2)
        feitas = []
        for config in plano["rede"][:3]:
            for rep in range(1, config["repeticoes"] + 1):
                feitas.append(medir_rede.linha_de_exemplo(config, rep))
        pendentes = medir_rede.pendentes_rede(plano["rede"], feitas)
        self.assertEqual(len(pendentes), len(plano["rede"]) - 3)
        self.assertEqual(medir_rede.pendentes_rede(plano["rede"], feitas + [
            medir_rede.linha_de_exemplo(c, r) for c in plano["rede"]
            for r in range(1, c["repeticoes"] + 1)]), [])


if __name__ == "__main__":
    unittest.main()
