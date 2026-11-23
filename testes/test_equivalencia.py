"""
Testes de equivalência: as versões sequencial (refatorada), paralela e
distribuída produzem a mesma grade da versão do professor em toda geração.

Com as melhorias do modelo ligadas (bots e resistência individual) não há
referência do professor; nesse caso a paralela e a distribuída são comparadas
com a sequencial refatorada, que já foi conferida contra o professor.
"""

import unittest

from comum.parametros import ParametrosSimulacao
from sequencial import fakenews_sequencial as sequencial
from paralelo import fakenews_paralelo as paralelo
from distribuido import executar_local
from auxiliares import Gravador, geracoes_do_professor


def gravar(funcao, parametros, **opcoes):
    """Executa uma versão sem imprimir e devolve as grades de cada geração."""
    gravador = Gravador(parametros.linhas, parametros.colunas)
    resultado = funcao(parametros, mostrar=False, ao_fim_da_geracao=gravador, **opcoes)
    return gravador.grades, resultado


# Cenários pequenos, escolhidos para exercitar a divisão não exata das linhas,
# grades estreitas e a parada antecipada (limiar 3 morre em poucas gerações).
CENARIOS = [
    ParametrosSimulacao(linhas=23, colunas=17, geracoes=25, percentual_espalhadores=0.05, limiar=2),
    ParametrosSimulacao(linhas=12, colunas=30, geracoes=15, percentual_espalhadores=0.10, limiar=3),
    ParametrosSimulacao(linhas=9, colunas=1, geracoes=10, percentual_espalhadores=0.30, limiar=1),
]

COM_MELHORIAS = [
    ParametrosSimulacao(linhas=21, colunas=19, geracoes=20, percentual_espalhadores=0.04, limiar=2,
                        fracao_bots=0.01),
    ParametrosSimulacao(linhas=18, colunas=22, geracoes=20, percentual_espalhadores=0.08, limiar=2,
                        resistencia=(1, 3)),
    ParametrosSimulacao(linhas=16, colunas=16, geracoes=20, percentual_espalhadores=0.05, limiar=2,
                        fracao_bots=0.02, resistencia=(1, 4)),
]


def referencia(p):
    """Grades do professor para os parâmetros p (sem melhorias)."""
    return geracoes_do_professor(p.linhas, p.colunas, p.geracoes, p.percentual_espalhadores,
                                 p.limiar, p.semente)


class TestSequencialRefatorada(unittest.TestCase):

    def test_igual_ao_professor(self):
        for p in CENARIOS:
            with self.subTest(p=p):
                grades, resultado = gravar(sequencial.executar_simulacao, p)
                self.assertEqual(grades, referencia(p))
                self.assertEqual(resultado["geracoes_executadas"], len(grades))


class TestParalela(unittest.TestCase):

    def test_processos_igual_ao_professor(self):
        for p in CENARIOS:
            for trabalhadores in (1, 2, 3, 7):
                with self.subTest(p=p, trabalhadores=trabalhadores):
                    grades, _ = gravar(paralelo.executar_simulacao, p,
                                       trabalhadores=trabalhadores, modo="processos")
                    self.assertEqual(grades, referencia(p))

    def test_mais_trabalhadores_que_linhas(self):
        p = ParametrosSimulacao(linhas=4, colunas=9, geracoes=8, percentual_espalhadores=0.3, limiar=2)
        grades, _ = gravar(paralelo.executar_simulacao, p, trabalhadores=6, modo="processos")
        self.assertEqual(grades, referencia(p))

    def test_threads_igual_ao_professor(self):
        for p in CENARIOS:
            for trabalhadores in (1, 3):
                with self.subTest(p=p, trabalhadores=trabalhadores):
                    grades, _ = gravar(paralelo.executar_simulacao, p,
                                       trabalhadores=trabalhadores, modo="threads")
                    self.assertEqual(grades, referencia(p))

    def test_com_melhorias_igual_a_sequencial(self):
        for p in COM_MELHORIAS:
            esperado, _ = gravar(sequencial.executar_simulacao, p)
            for modo in ("processos", "threads"):
                with self.subTest(p=p, modo=modo):
                    grades, _ = gravar(paralelo.executar_simulacao, p, trabalhadores=3, modo=modo)
                    self.assertEqual(grades, esperado)


class TestDistribuida(unittest.TestCase):

    def test_igual_ao_professor(self):
        for p in CENARIOS:
            for workers in (1, 2, 3):
                for bits in (False, True):
                    with self.subTest(p=p, workers=workers, bits=bits):
                        grades, _ = gravar(executar_local.executar_local, p, workers=workers,
                                           bits=bits, verificar=True)
                        self.assertEqual(grades, referencia(p))

    def test_com_melhorias_igual_a_sequencial(self):
        for p in COM_MELHORIAS:
            esperado, _ = gravar(sequencial.executar_simulacao, p)
            with self.subTest(p=p):
                grades, _ = gravar(executar_local.executar_local, p, workers=3, bits=True,
                                   verificar=True)
                self.assertEqual(grades, esperado)

    def test_mais_workers_que_linhas_e_recusado(self):
        p = ParametrosSimulacao(linhas=2, colunas=5, geracoes=3, percentual_espalhadores=0.3, limiar=2)
        with self.assertRaises(ValueError):
            executar_local.executar_local(p, workers=3, mostrar=False)


if __name__ == "__main__":
    unittest.main()
