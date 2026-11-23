"""
Testes das melhorias 2 (estatísticas e perfil de tempo) e 3 (animação HTML).

As duas só observam a simulação: ligar qualquer uma delas não pode mudar a
grade de nenhuma geração, em nenhuma das versões. Além disso, os números que
elas gravam precisam bater com a simulação do professor.
"""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from comum import modelo
from comum.estatisticas import Estatisticas
from comum.parametros import ParametrosSimulacao
from comum.visualizacao import Animacao
from distribuido import executar_local
from paralelo import fakenews_paralelo as paralelo
from sequencial import fakenews_sequencial as sequencial
from sequencial import fakenews_sequencial_original as professor

try:
    from .auxiliares import Gravador, geracoes_do_professor
except ImportError:  # rodado com a pasta testes/ como raiz
    from auxiliares import Gravador, geracoes_do_professor

P = ParametrosSimulacao(linhas=14, colunas=11, geracoes=12, percentual_espalhadores=0.12, limiar=2)

# (nome, função, opções, nº de trabalhadores esperado no perfil)
VERSOES = [
    ("sequencial", sequencial.executar_simulacao, {}, 1),
    ("paralela_processos", paralelo.executar_simulacao,
     {"trabalhadores": 2, "modo": "processos"}, 2),
    ("paralela_threads", paralelo.executar_simulacao, {"trabalhadores": 2, "modo": "threads"}, 2),
    ("distribuida", executar_local.executar_local, {"workers": 2}, 2),
]


def contagem_do_professor(grade):
    c = professor.contar_estados(grade)
    return {"ignorantes": c[professor.IGNORANTE], "espalhadores": c[professor.ESPALHADOR],
            "inativos": c[professor.INATIVO], "bots": 0}


def decodificar_quadro(quadro):
    """Quadro da animação ('0'..'3' por célula) de volta para lista de inteiros."""
    return [ord(c) - 48 for c in quadro["celulas"]]


class TestMelhoriasNasQuatroVersoes(unittest.TestCase):
    """Uma execução por versão, com estatísticas e animação ligadas ao mesmo tempo."""

    @classmethod
    def setUpClass(cls):
        cls.referencia = geracoes_do_professor(P.linhas, P.colunas, P.geracoes,
                                               P.percentual_espalhadores, P.limiar, P.semente)
        cls.inicial = professor.criar_grade(P.linhas, P.colunas, P.percentual_espalhadores,
                                            P.semente)
        cls.execucoes = {}
        for nome, funcao, opcoes, trabalhadores in VERSOES:
            estatisticas = Estatisticas(nome, P, trabalhadores)
            animacao = Animacao(P.linhas, P.colunas, nome)
            gravador = Gravador(P.linhas, P.colunas)
            resultado = funcao(P, mostrar=False, ao_fim_da_geracao=gravador,
                               estatisticas=estatisticas, animacao=animacao, **opcoes)
            cls.execucoes[nome] = (estatisticas, animacao, gravador.grades, resultado,
                                   trabalhadores)

    def test_grade_nao_muda(self):
        for nome, (_, _, grades, _, _) in self.execucoes.items():
            with self.subTest(versao=nome):
                self.assertEqual(grades, self.referencia)

    def test_contagens_por_geracao_iguais_ao_professor(self):
        esperado = [dict(geracao=g + 1, **contagem_do_professor(grade))
                    for g, grade in enumerate(self.referencia)]
        for nome, (estatisticas, _, _, _, _) in self.execucoes.items():
            with self.subTest(versao=nome):
                self.assertEqual(estatisticas.geracoes, esperado)

    def test_perfil_por_trabalhador(self):
        for nome, (estatisticas, _, _, resultado, trabalhadores) in self.execucoes.items():
            with self.subTest(versao=nome):
                perfil = estatisticas.por_trabalhador
                self.assertEqual(sorted(t["trabalhador"] for t in perfil),
                                 list(range(trabalhadores)))
                for t in perfil:
                    for campo in ("calculo_s", "comunicacao_s", "espera_s"):
                        self.assertGreaterEqual(t[campo], 0)
                    if nome == "distribuida":
                        self.assertGreater(t["bytes_enviados"], 0)
                self.assertEqual(estatisticas.tempo_laco, resultado["tempo_laco"])
                self.assertEqual(estatisticas.tempo_total, resultado["tempo_total"])

    def test_um_quadro_por_geracao_com_a_grade_certa(self):
        esperado = [[c for linha in grade for c in linha]
                    for grade in [self.inicial] + self.referencia]
        for nome, (_, animacao, _, _, _) in self.execucoes.items():
            with self.subTest(versao=nome):
                self.assertEqual(animacao.passo, 1)  # grade pequena: sem amostragem
                self.assertEqual([q["geracao"] for q in animacao.quadros],
                                 list(range(len(self.referencia) + 1)))
                self.assertEqual([decodificar_quadro(q) for q in animacao.quadros], esperado)

    def test_salvar_grava_os_tres_csvs(self):
        estatisticas = self.execucoes["distribuida"][0]
        with tempfile.TemporaryDirectory() as pasta:
            estatisticas.salvar(pasta)
            arquivos = sorted(p.name for p in Path(pasta).iterdir())
            self.assertEqual(arquivos, ["distribuida_geracoes.csv", "distribuida_resumo.csv",
                                        "distribuida_trabalhadores.csv"])

            def ler(nome):
                with open(Path(pasta) / nome, encoding="utf-8", newline="") as arquivo:
                    leitor = csv.DictReader(arquivo)
                    return leitor.fieldnames, list(leitor)

            campos, linhas = ler("distribuida_geracoes.csv")
            self.assertEqual(campos, ["geracao", "ignorantes", "espalhadores", "inativos", "bots"])
            self.assertEqual(len(linhas), len(self.referencia))
            campos, linhas = ler("distribuida_trabalhadores.csv")
            self.assertEqual(campos, ["trabalhador", "calculo_s", "comunicacao_s", "espera_s",
                                      "bytes_enviados"])
            self.assertEqual(len(linhas), 2)
            campos, linhas = ler("distribuida_resumo.csv")
            self.assertEqual(len(linhas), 1)
            self.assertEqual(linhas[0]["versao"], "distribuida")
            self.assertEqual(int(linhas[0]["geracoes_executadas"]), len(self.referencia))
            for campo in ("tempo_laco_s", "tempo_total_s", "alcance_final", "desbalanceamento"):
                self.assertIn(campo, campos)


class TestResumo(unittest.TestCase):

    def test_numeros_feitos_a_mao(self):
        p = ParametrosSimulacao(linhas=10, colunas=10)  # 100 pessoas
        est = Estatisticas("teste", p, 2)
        est.registrar_geracao(1, [80, 15, 5, 0])
        est.registrar_geracao(2, [60, 25, 15, 0])   # pico
        est.registrar_geracao(3, [55, 5, 40, 0])
        est.registrar_trabalhador(0, 1.0, 0.1, 0.2)
        est.registrar_trabalhador(1, 3.0, 0.1, 0.0)
        res = est.resumo()
        self.assertEqual(res["pico_espalhadores"], 25)
        self.assertEqual(res["geracao_do_pico"], 2)
        self.assertAlmostEqual(res["alcance_final"], 0.45)    # 1 - 55/100
        self.assertAlmostEqual(res["desbalanceamento"], 1.5)  # 3,0 / média 2,0

    def test_sem_dados(self):
        self.assertEqual(Estatisticas("teste", ParametrosSimulacao()).resumo(), {})


class TestAnimacao(unittest.TestCase):

    def test_amostragem_de_grade_grande(self):
        linhas, colunas = 600, 400
        animacao = Animacao(linhas, colunas, lado_maximo=300)
        self.assertEqual(animacao.passo, 2)
        # Grade com estado = (i + j) % 3, para dar para conferir cada célula amostrada.
        grade = [[(i + j) % 3 for j in range(colunas)] for i in range(linhas)]
        animacao.adicionar(0, modelo.grade_para_plana(grade))
        celulas = decodificar_quadro(animacao.quadros[0])
        self.assertEqual(len(celulas), 300 * 200)
        esperado = [grade[i][j] for i in range(0, linhas, 2) for j in range(0, colunas, 2)]
        self.assertEqual(celulas, esperado)

    def test_html_tem_os_dados_legiveis(self):
        animacao = Animacao(3, 4, "teste")
        grade = [[0, 1, 2, 3], [1, 1, 0, 0], [2, 2, 2, 2]]
        animacao.adicionar(0, modelo.grade_para_plana(grade))
        animacao.adicionar(1, modelo.grade_para_plana([[2] * 4] * 3))
        with tempfile.TemporaryDirectory() as pasta:
            caminho = animacao.salvar(Path(pasta) / "sub" / "grade.html")
            texto = caminho.read_text(encoding="utf-8")
        linha = next(l for l in texto.splitlines() if l.startswith("const D = "))
        dados = json.loads(linha[len("const D = "):].rstrip(";"))
        self.assertEqual((dados["linhas"], dados["colunas"]), (3, 4))
        self.assertEqual([q["geracao"] for q in dados["quadros"]], [0, 1])
        self.assertEqual(dados["quadros"][0]["celulas"], "012311002222")
        self.assertEqual(dados["quadros"][1]["celulas"], "2" * 12)


if __name__ == "__main__":
    unittest.main()
