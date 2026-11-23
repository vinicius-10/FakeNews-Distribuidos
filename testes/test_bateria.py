"""
Testes da bateria de experimentos (`experimentos/bateria.py`).

O ponto mais delicado aqui é o **fatiamento por cenário**. As funções de análise
(`analisar.agrupar` e `analisar.verificar_equivalencia`) agrupam por
(versão, tamanho, workers) e comparam hashes por tamanho — elas foram escritas
para o `medir.py`, onde `percentual` e `limiar` são constantes. Numa bateria que
varia os dois, usar essas funções no CSV inteiro misturaria cenários diferentes
na mesma mediana e acusaria divergência falsa de hash. Os testes abaixo travam
esse comportamento.
"""

import json
import tempfile
import unittest
from pathlib import Path

from experimentos import analisar
from experimentos import bateria


def linha(versao, percentual, limiar, tamanho, workers, tempo, hash_grade="igual"):
    """Uma linha de medição no formato do CSV (campos que a análise usa)."""
    return {
        "versao": versao, "modo": "serial", "workers": workers,
        "linhas": tamanho, "colunas": tamanho,
        "geracoes_pedidas": 5, "geracoes_executadas": 5,
        "limiar": limiar, "percentual": percentual, "repeticao": 1,
        "tempo_laco_s": tempo, "tempo_total_s": tempo, "hash_grade": hash_grade,
        "ignorantes": 1, "espalhadores": 0, "inativos": 0, "bots": 0,
    }


class TestCenarios(unittest.TestCase):

    def test_produto_cartesiano_em_ordem_deterministica(self):
        cenarios = bateria.montar_cenarios([0.01, 0.10], [1, 3], [100, 200])
        self.assertEqual(len(cenarios), 8)  # 2 × 2 × 2
        # Ordem estável: percentual, depois limiar, depois tamanho.
        self.assertEqual(cenarios[0], bateria.Cenario(0.01, 1, 100))
        self.assertEqual(cenarios[1], bateria.Cenario(0.01, 1, 200))
        self.assertEqual(cenarios[2], bateria.Cenario(0.01, 3, 100))
        self.assertEqual(cenarios[-1], bateria.Cenario(0.10, 3, 200))

    def test_nome_e_dict_identificam_o_cenario(self):
        c = bateria.Cenario(percentual=0.05, limiar=2, tamanho=300)
        self.assertEqual(c.nome, "p0.05_l2_300x300")
        self.assertEqual(c.como_dict(),
                         {"linhas": 300, "colunas": 300, "percentual": 0.05, "limiar": 2})

    def test_cenario_e_imutavel(self):
        c = bateria.Cenario(0.05, 2, 100)
        with self.assertRaises(Exception):
            c.limiar = 3


class TestPlano(unittest.TestCase):

    def test_seriais_uma_vez_por_cenario_e_paralelas_por_worker(self):
        cenarios = [bateria.Cenario(0.05, 2, 100)]
        versoes = ("sequencial", "paralela_processos")
        plano = bateria.montar_plano(cenarios, versoes, [1, 2, 4])
        # sequencial 1 config + paralela 3 configs = 4
        self.assertEqual(len(plano), 4)
        self.assertEqual([p[2] for p in plano], [1, 1, 2, 4])

    def test_seriais_nunca_repetem_por_worker(self):
        plano = bateria.montar_plano([bateria.Cenario(0.05, 2, 100)],
                                     ("sequencial", "sequencial_original"), [1, 2, 4])
        self.assertEqual(len(plano), 2)
        for _, versao, workers in plano:
            self.assertTrue(versao.startswith("sequencial"))
            self.assertEqual(workers, 1)

    def test_estimar_conta_aquecimento_e_repeticoes(self):
        plano = [("a", "b", 1)] * 4
        self.assertEqual(bateria.estimar(plano, repeticoes=3, aquecimento=1), 16)


class TestFatiarPorCenario(unittest.TestCase):
    """O fatiamento é o que impede misturar percentuais e limiares diferentes."""

    def test_separa_por_percentual_e_limiar(self):
        c1 = bateria.Cenario(0.01, 3, 200)
        c2 = bateria.Cenario(0.10, 3, 200)
        linhas = [
            linha("sequencial", 0.01, 3, 200, 1, 0.1),
            linha("sequencial", 0.10, 3, 200, 1, 0.9),
        ]
        fatias = bateria.fatiar_por_cenario(linhas, [c1, c2])
        self.assertEqual(len(fatias[c1]), 1)
        self.assertEqual(len(fatias[c2]), 1)
        self.assertEqual(fatias[c1][0]["tempo_laco_s"], 0.1)
        self.assertEqual(fatias[c2][0]["tempo_laco_s"], 0.9)

    def test_sem_fatiar_a_mediana_sairia_errada(self):
        """
        Prova por que o fatiamento existe.

        Sem separar os cenários, `analisar.agrupar` junta percentuais diferentes
        sob a mesma chave (versão, tamanho, workers) e a mediana vira a média de
        dois trabalhos que não têm nada a ver.
        """
        linhas = [
            linha("sequencial", 0.01, 3, 200, 1, 0.1),
            linha("sequencial", 0.10, 3, 200, 1, 0.9),
        ]
        misturado = analisar.agrupar(linhas)
        self.assertEqual(misturado[("sequencial", 200, 1)]["repeticao"], 2)
        self.assertAlmostEqual(misturado[("sequencial", 200, 1)]["mediana"], 0.5)

        # Fatiado, cada cenário reporta o próprio número.
        c1 = bateria.Cenario(0.01, 3, 200)
        c2 = bateria.Cenario(0.10, 3, 200)
        fatias = bateria.fatiar_por_cenario(linhas, [c1, c2])
        self.assertAlmostEqual(bateria.resumir_cenario(fatias[c1])[0]["mediana"], 0.1)
        self.assertAlmostEqual(bateria.resumir_cenario(fatias[c2])[0]["mediana"], 0.9)

    def test_equivalencia_falsa_sem_fatiar(self):
        """
        Dois percentuais produzem grades diferentes por definição.

        Comparados juntos, `verificar_equivalencia` acusaria divergência que não
        existe; fatiado por cenário, cada um fecha consigo mesmo.
        """
        linhas = [
            linha("sequencial", 0.01, 3, 200, 1, 0.1, hash_grade="aaa"),
            linha("sequencial", 0.10, 3, 200, 1, 0.9, hash_grade="bbb"),
        ]
        ok_misturado, divergencias, _ = analisar.verificar_equivalencia(linhas)
        self.assertFalse(ok_misturado)
        self.assertTrue(divergencias)

        fatias = bateria.fatiar_por_cenario(
            linhas, [bateria.Cenario(0.01, 3, 200), bateria.Cenario(0.10, 3, 200)])
        for cenario, fatia in fatias.items():
            ok, divs, _ = analisar.verificar_equivalencia(fatia)
            self.assertTrue(ok, f"cenário {cenario.nome} deveria fechar")
            self.assertEqual(divs, [])


class TestResumo(unittest.TestCase):

    def test_speedup_usa_a_sequencial_do_mesmo_cenario(self):
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.0),
            linha("paralela_processos", 0.05, 2, 100, 2, 0.5),
        ]
        resumo = {r["versao"]: r for r in bateria.resumir_cenario(linhas)}
        self.assertAlmostEqual(resumo["paralela_processos"]["speedup"], 2.0)
        self.assertAlmostEqual(resumo["paralela_processos"]["eficiencia"], 1.0)
        self.assertAlmostEqual(resumo["sequencial"]["speedup"], 1.0)

    def test_um_worker_perto_de_1_passa_na_conferencia(self):
        """1 worker com 5% de diferença da sequencial é ruído normal: nada a avisar."""
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.0),
            linha("paralela_processos", 0.05, 2, 100, 1, 1.05),
            linha("distribuida_local", 0.05, 2, 100, 1, 0.96),
        ]
        self.assertEqual(bateria.conferir_um_worker(bateria.resumir_cenario(linhas)), [])

    def test_um_worker_com_speedup_absurdo_e_apontado(self):
        """
        Invariante contra o outlier que já apareceu: 1 worker não tem paralelismo,
        então um speedup de 1,30 (ou 0,70) tem de ser apontado para investigar.
        """
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.30),
            linha("paralela_processos", 0.05, 2, 100, 1, 1.0),   # speedup 1,30
            linha("distribuida_bits", 0.05, 2, 100, 1, 1.30 / 0.7),  # speedup 0,70
            linha("paralela_processos", 0.05, 2, 100, 2, 0.5),   # 2 workers: não conferido
        ]
        fora = dict(bateria.conferir_um_worker(bateria.resumir_cenario(linhas)))
        self.assertEqual(set(fora), {"paralela_processos", "distribuida_bits"})
        self.assertAlmostEqual(fora["paralela_processos"], 1.30)
        self.assertAlmostEqual(fora["distribuida_bits"], 0.70)

    def test_threads_com_1_worker_nao_sao_conferidas(self):
        """As threads ficam abaixo de 1 pelo GIL; isso é o resultado, não um erro."""
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.0),
            linha("paralela_threads", 0.05, 2, 100, 1, 1.4),
        ]
        self.assertEqual(bateria.conferir_um_worker(bateria.resumir_cenario(linhas)), [])

    def test_sem_referencia_sequencial_o_speedup_e_none(self):
        linhas = [linha("paralela_processos", 0.05, 2, 100, 2, 0.5)]
        resumo = bateria.resumir_cenario(linhas)
        self.assertIsNone(resumo[0]["speedup"])
        self.assertIsNone(resumo[0]["eficiencia"])


class TestRelatorio(unittest.TestCase):

    def test_relatorio_tem_secao_por_cenario_e_veredito(self):
        cenarios = [bateria.Cenario(0.01, 3, 200), bateria.Cenario(0.10, 3, 200)]
        linhas = []
        for c in cenarios:
            linhas.append(linha("sequencial", c.percentual, c.limiar, 200, 1, 1.0, "h"))
            linhas.append(linha("paralela_processos", c.percentual, c.limiar, 200, 2, 0.5, "h"))

        texto, divergencias = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",),
                                                      repeticoes=5)
        self.assertEqual(divergencias, 0)
        for c in cenarios:
            self.assertIn(f"## {c.nome}", texto)
        self.assertIn("mesma grade final", texto)
        self.assertIn("Veredito geral", texto)

    def test_relatorio_avisa_quando_repeticao_e_pouca(self):
        cenarios = [bateria.Cenario(0.05, 2, 100)]
        linhas = [linha("sequencial", 0.05, 2, 100, 1, 1.0)]
        texto, _ = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",), repeticoes=1)
        self.assertIn("indicativos", texto)

    def test_relatorio_aponta_um_worker_fora_da_faixa(self):
        cenarios = [bateria.Cenario(0.05, 2, 100)]
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.3),
            linha("paralela_processos", 0.05, 2, 100, 1, 1.0),
        ]
        texto, divergencias = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",),
                                                      repeticoes=5)
        self.assertEqual(divergencias, 0)
        self.assertIn("Speedup com 1 worker fora", texto)
        self.assertIn("1 configuração(ões) com 1 worker", texto)

    def test_relatorio_avisa_abaixo_de_5_repeticoes(self):
        """O CONTRIBUTING pede pelo menos 5 repetições para números de relatório."""
        cenarios = [bateria.Cenario(0.05, 2, 100)]
        linhas = [linha("sequencial", 0.05, 2, 100, 1, 1.0)]
        texto_3, _ = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",), repeticoes=3)
        texto_5, _ = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",), repeticoes=5)
        self.assertIn("indicativos", texto_3)
        self.assertNotIn("indicativos", texto_5)

    def test_relatorio_denuncia_divergencia(self):
        cenarios = [bateria.Cenario(0.05, 2, 100)]
        linhas = [
            linha("sequencial", 0.05, 2, 100, 1, 1.0, "aaa"),
            linha("paralela_processos", 0.05, 2, 100, 2, 0.5, "bbb"),
        ]
        texto, divergencias = bateria.gerar_relatorio(linhas, cenarios, ("sequencial",),
                                                      repeticoes=5)
        self.assertEqual(divergencias, 1)
        self.assertIn("divergência", texto)


class TestExportar(unittest.TestCase):

    def test_json_tem_tudo_que_a_rede_precisa(self):
        cenarios = bateria.montar_cenarios([0.01, 0.10], [2], [200])
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "sub" / "cenarios.json"
            caminho = bateria.exportar_cenarios(cenarios, ("sequencial",), [1, 2],
                                                20, 42, destino)
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        self.assertEqual(dados["geracoes"], 20)
        self.assertEqual(dados["semente"], 42)
        self.assertEqual(len(dados["cenarios"]), 2)
        primeiro = dados["cenarios"][0]
        for chave in ("linhas", "colunas", "percentual", "limiar", "geracoes", "semente"):
            self.assertIn(chave, primeiro)
        self.assertEqual(primeiro["linhas"], 200)
        self.assertEqual(primeiro["percentual"], 0.01)


if __name__ == "__main__":
    unittest.main()
