"""
Testes da verificação da seção 3.4.2 (`experimentos/verificar_342.py`).

Só as funções puras: cálculo de desvio e montagem das tabelas em markdown. As
medições de tempo em si levam minutos e não entram na suíte.
"""

import unittest

from experimentos import verificar_342 as v


class TestDesvio(unittest.TestCase):

    def test_desvio_positivo_e_negativo(self):
        self.assertAlmostEqual(v._desvio(4.19, 4.16), (4.19 - 4.16) / 4.16 * 100)
        self.assertAlmostEqual(v._desvio(0.819, 0.855), (0.819 - 0.855) / 0.855 * 100)

    def test_sem_referencia_devolve_none(self):
        self.assertIsNone(v._desvio(1.0, None))
        self.assertIsNone(v._desvio(None, 1.0))

    def test_referencia_zero_nao_divide(self):
        """Custo publicado 0 não pode virar ZeroDivisionError."""
        self.assertIsNone(v._desvio(1.0, 0))


class TestTabelasMarkdown(unittest.TestCase):

    def _medido_tabela1(self):
        return {
            500: {"celulas": 250_000, "tempo": 4.19, "por_geracao": 0.209,
                  "por_celula_us": 0.84, "geracoes": 20, "repeticoes": 3},
            2000: {"celulas": 4_000_000, "tempo": 67.94, "por_geracao": 3.397,
                   "por_celula_us": 0.85, "geracoes": 20, "repeticoes": 3},
        }

    def test_tabela1_tem_linha_por_tamanho_e_desvio(self):
        texto = v._tabela1_md(self._medido_tabela1())
        linhas = [l for l in texto.splitlines() if l.startswith("| 500") or l.startswith("| 2000")]
        self.assertEqual(len(linhas), 2)
        # 500 está publicado (4,16) -> tem desvio; 2000 também (65,88).
        self.assertIn("%", linhas[0])
        self.assertIn("%", linhas[1])

    def test_tabela1_sem_publicado_usa_traco(self):
        medido = {123: {"celulas": 15_129, "tempo": 1.0, "por_geracao": 0.05,
                        "por_celula_us": 0.5, "geracoes": 20, "repeticoes": 1}}
        texto = v._tabela1_md(medido)
        self.assertIn("—", texto)  # sem valor publicado, sem desvio

    def test_tabela2_soma_participacoes_em_100(self):
        medido = {"varredura": 0.641, "copia": 0.175, "contagem": 0.044,
                  "total": 0.860, "repeticoes": 5}
        texto = v._tabela2_md(medido)
        # A participação usa o total como denominador; as três etapas são
        # 0,641+0,175+0,044 = 0,860, então devem somar 100%. Cada valor é
        # arredondado a uma casa decimal na tabela, então a soma pode desviar
        # frações de ponto — daí a tolerância.
        participacoes = [float(l.split("|")[3]) for l in texto.splitlines()
                         if l.startswith("| Varredura") or l.startswith("| Cópia")
                         or l.startswith("| Contagem")]
        self.assertEqual(len(participacoes), 3)
        self.assertAlmostEqual(sum(participacoes), 100.0, delta=0.3)

    def test_tabela2_tem_as_quatro_etapas(self):
        medido = {"varredura": 0.6, "copia": 0.2, "contagem": 0.05,
                  "total": 0.85, "repeticoes": 5}
        texto = v._tabela2_md(medido)
        for rotulo in ("Varredura das células", "Cópia da grade",
                       "Contagem dos estados", "Total"):
            self.assertIn(rotulo, texto)


class TestReferenciasPublicadas(unittest.TestCase):
    """As referências do trabalho não podem ser alteradas por acidente."""

    def test_tabela1_publicada(self):
        self.assertAlmostEqual(v.PUBLICADO_TABELA1[500]["tempo"], 4.16)
        self.assertAlmostEqual(v.PUBLICADO_TABELA1[1000]["tempo"], 16.46)
        self.assertAlmostEqual(v.PUBLICADO_TABELA1[2000]["tempo"], 65.88)

    def test_tabela2_publicada_fecha_no_total(self):
        etapas = (v.PUBLICADO_TABELA2["varredura"] + v.PUBLICADO_TABELA2["copia"]
                  + v.PUBLICADO_TABELA2["contagem"])
        # Publicado: 0,638 + 0,179 + 0,038 = 0,855.
        self.assertAlmostEqual(etapas, v.PUBLICADO_TABELA2["total"], places=3)


class TestAvisoDeVersao(unittest.TestCase):
    """O padrão do projeto é Python 3.11; outra versão precisa avisar."""

    def test_versao_padrao_nao_avisa(self):
        self.assertIsNone(v.aviso_de_versao("3.11.7"))
        self.assertIsNone(v.aviso_de_versao("3.11.0"))

    def test_versao_diferente_avisa(self):
        for versao in ("3.12.10", "3.13.5", "3.10.13"):
            with self.subTest(versao=versao):
                aviso = v.aviso_de_versao(versao)
                self.assertIsNotNone(aviso)
                self.assertIn(versao, aviso)
                self.assertIn(v.VERSAO_PADRAO, aviso)

    def test_sem_argumento_usa_a_versao_do_ambiente(self):
        """Chamada sem argumento (como o main faz) não pode explodir."""
        import platform
        aviso = v.aviso_de_versao()
        if platform.python_version().startswith("3.11."):
            self.assertIsNone(aviso)
        else:
            self.assertIsNotNone(aviso)


if __name__ == "__main__":
    unittest.main()
