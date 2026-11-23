"""
Testes da saída impressa.

A saída no mesmo formato do professor permite comparar as versões lado a lado
(e é o que aparece no vídeo). Aqui:
- a sequencial refatorada imprime exatamente o mesmo texto do professor, com e
  sem `mostrar_grade`, tirando só o título e as linhas de tempo;
- a paralela e a distribuída imprimem as mesmas linhas de geração, o mesmo
  aviso de fim e o mesmo resultado final da sequencial refatorada.
"""

import unittest

from comum.parametros import ParametrosSimulacao
from distribuido import executar_local
from paralelo import fakenews_paralelo as paralelo
from sequencial import fakenews_sequencial as sequencial
from sequencial import fakenews_sequencial_original as professor

try:
    from .auxiliares import capturar_saida
except ImportError:  # rodado com a pasta testes/ como raiz
    from auxiliares import capturar_saida

# O primeiro vai até o fim das gerações; o segundo para antes (limiar 3).
CENARIOS = [
    ParametrosSimulacao(linhas=12, colunas=9, geracoes=6, percentual_espalhadores=0.2, limiar=2),
    ParametrosSimulacao(linhas=12, colunas=30, geracoes=15, percentual_espalhadores=0.10, limiar=3),
]


def sem_titulo_e_tempos(texto):
    """Tira o título (cada versão tem o seu) e os tempos (mudam a cada execução)."""
    return [linha for linha in texto.splitlines()
            if not linha.startswith(("=== SIMULAÇÃO", "Tempo"))]


def geracoes_e_resultado(texto):
    """Só as linhas que dependem da simulação: gerações, aviso de fim e resultado final."""
    escolhidas = []
    no_resultado = False
    for linha in texto.splitlines():
        if linha == "=== RESULTADO FINAL ===":
            no_resultado = True
        if no_resultado and not linha.startswith("Tempo"):
            escolhidas.append(linha)
        elif linha.startswith("Geração") or linha.startswith("A propagação terminou"):
            escolhidas.append(linha)
    return escolhidas


def saida_do_professor(p, mostrar_grade=False):
    texto, _ = capturar_saida(professor.executar_simulacao, p.linhas, p.colunas, p.geracoes,
                              p.percentual_espalhadores, p.limiar, mostrar_grade)
    return texto


class TestSaidaSequencial(unittest.TestCase):

    def test_igual_ao_professor(self):
        for p in CENARIOS:
            for mostrar_grade in (False, True):
                with self.subTest(p=p, mostrar_grade=mostrar_grade):
                    texto, _ = capturar_saida(sequencial.executar_simulacao, p,
                                              mostrar_grade=mostrar_grade)
                    self.assertEqual(sem_titulo_e_tempos(texto),
                                     sem_titulo_e_tempos(saida_do_professor(p, mostrar_grade)))

    def test_cenario_com_parada_antecipada(self):
        # Garante que o segundo cenário de fato exercita o aviso de fim.
        self.assertIn("A propagação terminou", saida_do_professor(CENARIOS[1]))


class TestSaidaParalelaEDistribuida(unittest.TestCase):

    def test_mesmas_linhas_da_sequencial(self):
        for p in CENARIOS:
            esperado = geracoes_e_resultado(capturar_saida(sequencial.executar_simulacao, p)[0])
            versoes = {
                "processos": lambda: paralelo.executar_simulacao(p, trabalhadores=2,
                                                                 modo="processos"),
                "threads": lambda: paralelo.executar_simulacao(p, trabalhadores=2,
                                                               modo="threads"),
                "distribuida": lambda: executar_local.executar_local(p, workers=2),
            }
            for nome, executar in versoes.items():
                with self.subTest(p=p, versao=nome):
                    texto, _ = capturar_saida(executar)
                    self.assertEqual(geracoes_e_resultado(texto), esperado)


if __name__ == "__main__":
    unittest.main()
