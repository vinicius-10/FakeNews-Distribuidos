"""
Funções de apoio dos testes: referência do professor, comparação de grades e
captura do que é impresso.

A referência de comportamento é o código sequencial do professor
(sequencial/fakenews_sequencial_original.py), usado aqui sem nenhuma alteração.
"""

import contextlib
import io

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
