"""
Testes do protocolo de mensagens da versão distribuída.

O ponto principal é que recv pode devolver só parte de uma mensagem; o
protocolo precisa remontá-la a partir do tamanho que vem no cabeçalho.
"""

import socket
import threading
import unittest

from distribuido import protocolo


class TestProtocolo(unittest.TestCase):

    def setUp(self):
        self.a, self.b = socket.socketpair()
        self.a.settimeout(5)
        self.b.settimeout(5)

    def tearDown(self):
        self.a.close()
        self.b.close()

    def test_ida_e_volta(self):
        protocolo.enviar(self.a, protocolo.HALO, b"\x00\x01\x02")
        self.assertEqual(protocolo.receber(self.b), (protocolo.HALO, b"\x00\x01\x02"))

    def test_mensagem_vazia(self):
        protocolo.enviar(self.a, protocolo.DECISAO, b"")
        self.assertEqual(protocolo.receber(self.b), (protocolo.DECISAO, b""))

    def test_json(self):
        protocolo.enviar_json(self.a, protocolo.INICIO, {"linhas": 3, "nome": "ação"})
        tipo, dados = protocolo.receber_json(self.b)
        self.assertEqual(tipo, protocolo.INICIO)
        self.assertEqual(dados, {"linhas": 3, "nome": "ação"})

    def test_mensagem_grande_chega_inteira(self):
        carga = bytes(range(256)) * 4000  # ~1 MB: o recv devolve em pedaços
        envio = threading.Thread(target=protocolo.enviar, args=(self.a, protocolo.FAIXA, carga))
        envio.start()
        tipo, recebido = protocolo.receber(self.b)
        envio.join()
        self.assertEqual(tipo, protocolo.FAIXA)
        self.assertEqual(recebido, carga)

    def test_conexao_fechada_no_meio(self):
        self.a.sendall(b"\x03\x00\x00\x00\x10abc")  # anuncia 16 bytes e manda 3
        self.a.close()
        with self.assertRaises(ConnectionError):
            protocolo.receber(self.b)

    def test_tipo_esperado(self):
        protocolo.enviar(self.a, protocolo.HALO, b"x")
        with self.assertRaises(protocolo.ErroProtocolo):
            protocolo.receber(self.b, esperado=protocolo.CONTAGEM)


if __name__ == "__main__":
    unittest.main()
