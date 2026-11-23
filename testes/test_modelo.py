"""
Testes do núcleo comum (comum/modelo.py).

O núcleo é o código que as três versões usam para calcular uma geração. Se ele
não reproduzir exatamente a transição do professor, nenhuma versão reproduz.
"""

import random
import unittest

from sequencial import fakenews_sequencial_original as professor
from comum import modelo
from comum.modelo import BOT, ESPALHADOR, IGNORANTE, INATIVO


def proxima_com_nucleo(grade, limiar, limiares=None):
    """Calcula uma geração inteira com o núcleo, numa faixa única."""
    linhas, colunas = len(grade), len(grade[0])
    atual = modelo.grade_para_plana(grade)
    nova = bytearray(len(atual))
    plana_limiares = modelo.grade_para_plana(limiares) if limiares else None
    modelo.calcular_faixa(atual, nova, colunas, 1, linhas + 1, limiar, plana_limiares)
    return modelo.plana_para_lista(nova, linhas, colunas)


class TestNucleoIgualAoProfessor(unittest.TestCase):
    """Sem as melhorias do modelo, o núcleo precisa ser idêntico ao professor."""

    def test_grades_aleatorias(self):
        sorteio = random.Random(7)
        for _ in range(60):
            linhas = sorteio.randint(1, 12)
            colunas = sorteio.randint(1, 12)
            grade = [[sorteio.choice((IGNORANTE, ESPALHADOR, INATIVO)) for _ in range(colunas)]
                     for _ in range(linhas)]
            limiar = sorteio.randint(0, 9)
            with self.subTest(linhas=linhas, colunas=colunas, limiar=limiar):
                self.assertEqual(proxima_com_nucleo(grade, limiar),
                                 professor.proxima_geracao(grade, limiar))

    def test_casos_de_borda(self):
        casos = {
            "1x1 espalhador": [[ESPALHADOR]],
            "1x1 ignorante": [[IGNORANTE]],
            "uma linha": [[ESPALHADOR, IGNORANTE, ESPALHADOR, IGNORANTE]],
            "uma coluna": [[ESPALHADOR], [IGNORANTE], [ESPALHADOR]],
            "só espalhadores": [[ESPALHADOR] * 4 for _ in range(3)],
            "nenhum espalhador": [[IGNORANTE] * 4 for _ in range(3)],
            "cantos": [[ESPALHADOR, IGNORANTE, ESPALHADOR],
                       [IGNORANTE, IGNORANTE, IGNORANTE],
                       [ESPALHADOR, IGNORANTE, ESPALHADOR]],
        }
        for nome, grade in casos.items():
            for limiar in range(0, 9):
                with self.subTest(caso=nome, limiar=limiar):
                    self.assertEqual(proxima_com_nucleo(grade, limiar),
                                     professor.proxima_geracao(grade, limiar))

    def test_varias_geracoes_com_a_grade_do_professor(self):
        for limiar in (1, 2, 3):
            grade = professor.criar_grade(30, 25, 0.05, 42)
            for geracao in range(15):
                esperado = professor.proxima_geracao(grade, limiar)
                with self.subTest(limiar=limiar, geracao=geracao):
                    self.assertEqual(proxima_com_nucleo(grade, limiar), esperado)
                grade = esperado

    def test_faixas_calculadas_separadamente_dao_a_grade_inteira(self):
        grade = professor.criar_grade(20, 15, 0.2, 42)
        atual = modelo.grade_para_plana(grade)
        nova = bytearray(len(atual))
        for ini, fim in modelo.dividir_em_faixas(20, 6):
            modelo.calcular_faixa(atual, nova, 15, ini + 1, fim + 1, 2)
        self.assertEqual(modelo.plana_para_lista(nova, 20, 15),
                         professor.proxima_geracao(grade, 2))


class TestConversoesEFaixas(unittest.TestCase):
    """Conversão lista <-> vetor de bytes e divisão das linhas."""

    def test_ida_e_volta(self):
        grade = professor.criar_grade(7, 5, 0.3, 42)
        plana = modelo.grade_para_plana(grade)
        self.assertEqual(len(plana), (7 + 2) * 5)
        self.assertEqual(modelo.plana_para_lista(plana, 7, 5), grade)

    def test_moldura_zerada(self):
        plana = modelo.grade_para_plana([[ESPALHADOR] * 3 for _ in range(2)])
        self.assertEqual(bytes(plana[:3]), bytes(3))
        self.assertEqual(bytes(plana[-3:]), bytes(3))

    def test_dividir_em_faixas(self):
        for linhas in (1, 2, 5, 10, 17):
            for partes in (1, 2, 3, 4, 7, 20):
                faixas = modelo.dividir_em_faixas(linhas, partes)
                with self.subTest(linhas=linhas, partes=partes):
                    self.assertEqual(len(faixas), partes)
                    self.assertEqual(faixas[0][0], 0)
                    self.assertEqual(faixas[-1][1], linhas)
                    for (a, b), (c, _) in zip(faixas, faixas[1:]):
                        self.assertEqual(b, c)
                    tamanhos = [fim - ini for ini, fim in faixas]
                    self.assertLessEqual(max(tamanhos) - min(tamanhos), 1)

    def test_contar_faixa(self):
        grade = [[IGNORANTE, ESPALHADOR], [INATIVO, BOT], [ESPALHADOR, ESPALHADOR]]
        plana = modelo.grade_para_plana(grade)
        self.assertEqual(modelo.contar_faixa(plana, 2, 1, 4), [1, 3, 1, 1])
        self.assertEqual(modelo.contar_faixa(plana, 2, 2, 3), [0, 0, 1, 1])


class TestBordaEmBits(unittest.TestCase):
    """Melhoria: linha de borda compactada, 1 bit por célula."""

    def test_ida_e_volta(self):
        sorteio = random.Random(3)
        for colunas in (1, 7, 8, 9, 16, 33):
            linha = [sorteio.choice((IGNORANTE, ESPALHADOR, INATIVO, BOT)) for _ in range(colunas)]
            origem = bytearray(linha)
            dados = modelo.empacotar_bits(origem, 0, colunas)
            self.assertEqual(len(dados), (colunas + 7) // 8)
            destino = bytearray(colunas)
            modelo.desempacotar_bits(dados, destino, 0, colunas)
            esperado = [modelo.CONTA_COMO_ESPALHADOR[v] for v in linha]
            with self.subTest(colunas=colunas):
                self.assertEqual(list(destino), esperado)


class TestMelhoriasDoModelo(unittest.TestCase):
    """Melhorias: bots e resistência individual."""

    def test_bot_continua_bot_e_conta_como_espalhador(self):
        grade = [[BOT, IGNORANTE, IGNORANTE],
                 [IGNORANTE, IGNORANTE, IGNORANTE]]
        nova = proxima_com_nucleo(grade, 1)
        self.assertEqual(nova, [[BOT, ESPALHADOR, IGNORANTE],
                                [ESPALHADOR, ESPALHADOR, IGNORANTE]])
        nova = proxima_com_nucleo(nova, 1)
        self.assertEqual(nova[0][0], BOT)

    def test_limiar_individual(self):
        grade = [[ESPALHADOR, IGNORANTE, ESPALHADOR]]
        # A célula do meio tem 2 vizinhos espalhadores.
        self.assertEqual(proxima_com_nucleo(grade, 9, [[1, 2, 1]])[0][1], ESPALHADOR)
        self.assertEqual(proxima_com_nucleo(grade, 9, [[1, 3, 1]])[0][1], IGNORANTE)

    def test_grade_inicial_sem_melhorias_igual_ao_professor(self):
        grade = modelo.criar_grade_inicial(40, 30, 0.05, 42)
        self.assertEqual(grade, professor.criar_grade(40, 30, 0.05, 42))

    def test_bots_e_limiares_reproduziveis(self):
        a = modelo.criar_grade_inicial(30, 30, 0.05, 42, fracao_bots=0.02)
        b = modelo.criar_grade_inicial(30, 30, 0.05, 42, fracao_bots=0.02)
        self.assertEqual(a, b)
        self.assertTrue(any(BOT in linha for linha in a))
        la = modelo.criar_limiares(30, 30, 1, 4, 42)
        self.assertEqual(la, modelo.criar_limiares(30, 30, 1, 4, 42))
        self.assertTrue(all(1 <= v <= 4 for linha in la for v in linha))


if __name__ == "__main__":
    unittest.main()
