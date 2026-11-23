"""
Testes das fórmulas usadas na análise dos experimentos (experimentos/analisar.py).

Os valores esperados foram calculados à mão. `analisar.py` só importa a
biblioteca padrão no topo (o matplotlib é importado dentro de
`gerar_graficos`), então estes testes não dependem de nada instalado.
"""

import math
import unittest

from experimentos import analisar


class TestSpeedupEficiencia(unittest.TestCase):

    def test_speedup(self):
        self.assertEqual(analisar.speedup(10, 2), 5)
        self.assertEqual(analisar.speedup(3, 4), 0.75)  # mais lento que a base

    def test_speedup_com_tempo_zero_e_nan(self):
        self.assertTrue(math.isnan(analisar.speedup(10, 0)))

    def test_eficiencia(self):
        self.assertEqual(analisar.eficiencia(6, 8), 0.75)
        self.assertEqual(analisar.eficiencia(4, 4), 1.0)
        self.assertTrue(math.isnan(analisar.eficiencia(4, 0)))


class TestFracaoSerial(unittest.TestCase):

    def test_karp_flatt(self):
        # f = (1/3,2 - 1/4) / (1 - 1/4) = 0,0625 / 0,75 = 0,08333...
        self.assertAlmostEqual(analisar.karp_flatt(3.2, 4), 1 / 12)

    def test_karp_flatt_extremos(self):
        self.assertAlmostEqual(analisar.karp_flatt(8, 8), 0.0)  # speedup ideal: nada serial
        self.assertAlmostEqual(analisar.karp_flatt(1, 8), 1.0)  # sem ganho: tudo serial
        self.assertIsNone(analisar.karp_flatt(1, 1))            # p = 1 não define f

    def test_amdahl(self):
        self.assertAlmostEqual(analisar.amdahl(0, 8), 8)    # tudo paralelizável
        self.assertAlmostEqual(analisar.amdahl(1, 8), 1)    # tudo serial
        self.assertAlmostEqual(analisar.amdahl(0.1, 4), 1 / (0.1 + 0.9 / 4))
        self.assertIsNone(analisar.amdahl(None, 4))

    def test_amdahl_desfaz_karp_flatt(self):
        # Karp-Flatt é a lei de Amdahl resolvida para f: ida e volta dá o mesmo S.
        for s, p in ((3.2, 4), (10.9, 24), (1.5, 2)):
            with self.subTest(s=s, p=p):
                self.assertAlmostEqual(analisar.amdahl(analisar.karp_flatt(s, p), p), s)

    def test_gustafson(self):
        self.assertEqual(analisar.gustafson(0, 8), 8)
        self.assertEqual(analisar.gustafson(1, 8), 1)
        self.assertAlmostEqual(analisar.gustafson(0.1, 4), 4 - 0.1 * 3)
        self.assertIsNone(analisar.gustafson(None, 4))


def medida(versao, linhas, workers, tempo, total=None, hash_grade="h"):
    """Uma linha no formato devolvido por `analisar.carregar`."""
    return {"versao": versao, "linhas": linhas, "workers": workers,
            "tempo_laco_s": tempo, "tempo_total_s": total, "hash_grade": hash_grade}


class TestAgregacao(unittest.TestCase):

    def test_agrupar_mediana_e_desvio(self):
        linhas = [medida("paralela_processos", 500, 4, t, t + 1) for t in (1.0, 3.0, 2.0)]
        linhas.append(medida("paralela_processos", 500, 8, 0.5))  # outro grupo
        resumo = analisar.agrupar(linhas)
        grupo = resumo[("paralela_processos", 500, 4)]
        self.assertEqual(grupo["repeticao"], 3)
        self.assertEqual(grupo["mediana"], 2.0)
        self.assertAlmostEqual(grupo["desvio"], 1.0)  # desvio amostral de 1, 2, 3
        self.assertEqual((grupo["minimo"], grupo["maximo"]), (1.0, 3.0))
        self.assertEqual(grupo["mediana_total"], 3.0)
        sozinho = resumo[("paralela_processos", 500, 8)]
        self.assertEqual(sozinho["desvio"], 0.0)       # uma medida só: sem desvio
        self.assertIsNone(sozinho["mediana_total"])    # sem tempo_total gravado

    def test_verificar_equivalencia_aceita_hashes_iguais(self):
        linhas = [medida("sequencial", 500, 1, 1.0, hash_grade="abc"),
                  medida("paralela_processos", 500, 4, 0.3, hash_grade="abc"),
                  medida("distribuida_local", 500, 4, 0.3, hash_grade="abc")]
        ok, divergencias, tamanhos = analisar.verificar_equivalencia(linhas)
        self.assertTrue(ok)
        self.assertEqual(divergencias, [])
        self.assertEqual(tamanhos, [500])

    def test_verificar_equivalencia_acusa_hash_divergente(self):
        linhas = [medida("sequencial", 500, 1, 1.0, hash_grade="abc"),
                  medida("paralela_processos", 500, 4, 0.3, hash_grade="abc"),
                  medida("distribuida_local", 500, 4, 0.3, hash_grade="xyz")]
        ok, divergencias, _ = analisar.verificar_equivalencia(linhas)
        self.assertFalse(ok)
        self.assertEqual(divergencias, [("distribuida_local", 500, 4, "xyz", "abc")])


if __name__ == "__main__":
    unittest.main()
