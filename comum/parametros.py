"""
Parâmetros da simulação e leitura pela linha de comando.

Todas as versões aceitam os mesmos parâmetros, com os mesmos padrões da
chamada no fim do código do professor (100 x 100, 50 gerações, 5% de
espalhadores, limiar 3).
"""

import argparse
from dataclasses import dataclass

from comum import modelo


@dataclass(frozen=True)
class ParametrosSimulacao:
    """Parâmetros de uma simulação (iguais para as três versões)."""

    linhas: int = 100
    colunas: int = 100
    geracoes: int = 50
    percentual_espalhadores: float = 0.05
    limiar: int = 3
    semente: int = 42
    # Melhorias do modelo; desligadas por padrão para reproduzir o professor.
    resistencia: tuple = None  # (limiar mínimo, limiar máximo) por célula
    fracao_bots: float = 0.0

    def validar(self):
        """Recusa valores que não fazem sentido, com uma mensagem clara."""
        if self.linhas < 1 or self.colunas < 1:
            raise ValueError("a grade precisa ter pelo menos 1 linha e 1 coluna")
        if self.geracoes < 1:
            raise ValueError("é preciso pelo menos 1 geração")
        if not 0 <= self.percentual_espalhadores <= 1 or not 0 <= self.fracao_bots <= 1:
            raise ValueError("percentuais vão de 0 a 1 (ex.: 0.05 = 5%)")
        if self.resistencia is not None:
            minimo, maximo = self.resistencia
            if not 0 <= minimo <= maximo <= 9:
                raise ValueError("a resistência é um intervalo de limiares entre 0 e 9")


def preparar_estado_inicial(parametros):
    """
    Gera a grade inicial (e os limiares individuais, se houver) em vetor de bytes.

    É chamado UMA vez, pelo processo principal (paralela) ou pelo coordenador
    (distribuída), antes de dividir a grade: nenhum worker sorteia nada.
    Devolve (grade, limiares), com limiares = None sem a melhoria.
    """
    parametros.validar()
    grade = modelo.criar_grade_inicial(parametros.linhas, parametros.colunas,
                                       parametros.percentual_espalhadores, parametros.semente,
                                       parametros.fracao_bots)
    limiares = None
    if parametros.resistencia is not None:
        minimo, maximo = parametros.resistencia
        limiares = modelo.grade_para_plana(
            modelo.criar_limiares(parametros.linhas, parametros.colunas, minimo, maximo,
                                  parametros.semente))
    return modelo.grade_para_plana(grade), limiares


def adicionar_argumentos(parser):
    """Acrescenta ao parser os parâmetros comuns da simulação."""
    padrao = ParametrosSimulacao()
    grupo = parser.add_argument_group("simulação")
    grupo.add_argument("--linhas", type=int, default=padrao.linhas)
    grupo.add_argument("--colunas", type=int, default=padrao.colunas)
    grupo.add_argument("--geracoes", type=int, default=padrao.geracoes)
    grupo.add_argument("--percentual", type=float, default=padrao.percentual_espalhadores,
                       help="fração inicial de espalhadores (0.05 = 5%%)")
    grupo.add_argument("--limiar", type=int, default=padrao.limiar,
                       help="vizinhos espalhadores necessários para convencer")
    grupo.add_argument("--semente", type=int, default=padrao.semente)
    grupo.add_argument("--resistencia", type=int, nargs=2, metavar=("MIN", "MAX"),
                       help="melhoria: limiar individual sorteado entre MIN e MAX")
    grupo.add_argument("--bots", type=float, default=0.0, metavar="FRACAO",
                       help="melhoria: fração de células que são bots (0.01 = 1%%)")
    saida = parser.add_argument_group("saída")
    saida.add_argument("--mostrar-grade", action="store_true",
                       help="imprime o canto da grade a cada geração (grades pequenas)")
    saida.add_argument("--estatisticas", metavar="PASTA",
                       help="melhoria: grava CSVs com as estatísticas e o perfil de tempo")
    saida.add_argument("--animacao", metavar="ARQUIVO.html",
                       help="melhoria: grava uma animação da grade (abre no navegador)")
    return parser


def parametros_de_argumentos(args):
    """Monta ParametrosSimulacao a partir do resultado do argparse."""
    return ParametrosSimulacao(
        linhas=args.linhas,
        colunas=args.colunas,
        geracoes=args.geracoes,
        percentual_espalhadores=args.percentual,
        limiar=args.limiar,
        semente=args.semente,
        resistencia=tuple(args.resistencia) if args.resistencia else None,
        fracao_bots=args.bots,
    )


def novo_parser(descricao):
    """Cria um parser já com os parâmetros comuns."""
    return adicionar_argumentos(argparse.ArgumentParser(description=descricao))
