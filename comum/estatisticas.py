"""
Melhoria "estatísticas e perfil de tempo".

Guarda a contagem de estados de cada geração e, de cada worker, quanto tempo
ele passou calculando, comunicando e esperando (barreira ou decisão do
coordenador). Esses números alimentam a análise de gargalos, de sincronização
e de custo de comunicação pedida no enunciado.
"""

import csv
from pathlib import Path

from comum.modelo import BOT, ESPALHADOR, IGNORANTE, INATIVO


class Estatisticas:
    """Acumula as estatísticas de uma execução e grava em CSV."""

    def __init__(self, versao, parametros, trabalhadores=1):
        self.versao = versao
        self.parametros = parametros
        self.trabalhadores = trabalhadores
        self.geracoes = []       # uma linha por geração
        self.por_trabalhador = []  # uma linha por worker
        self.tempo_laco = None
        self.tempo_total = None

    def registrar_geracao(self, geracao, contagem):
        """Guarda a contagem [ign, esp, inat, bots] de uma geração."""
        self.geracoes.append({
            "geracao": geracao,
            "ignorantes": contagem[IGNORANTE],
            "espalhadores": contagem[ESPALHADOR],
            "inativos": contagem[INATIVO],
            "bots": contagem[BOT],
        })

    def registrar_trabalhador(self, ident, calculo, comunicacao, espera, bytes_enviados=0):
        """Guarda o perfil de tempo de um worker (em segundos)."""
        self.por_trabalhador.append({
            "trabalhador": ident,
            "calculo_s": round(calculo, 6),
            "comunicacao_s": round(comunicacao, 6),
            "espera_s": round(espera, 6),
            "bytes_enviados": bytes_enviados,
        })

    def resumo(self):
        """Pico de espalhadores, alcance final e desbalanceamento de carga."""
        total = self.parametros.linhas * self.parametros.colunas
        res = {}
        if self.geracoes:
            pico = max(self.geracoes, key=lambda g: g["espalhadores"])
            final = self.geracoes[-1]
            res["pico_espalhadores"] = pico["espalhadores"]
            res["geracao_do_pico"] = pico["geracao"]
            # Alcance: fração da população que deixou de ser ignorante.
            res["alcance_final"] = 1 - final["ignorantes"] / total
        if self.por_trabalhador:
            calculos = [t["calculo_s"] for t in self.por_trabalhador]
            media = sum(calculos) / len(calculos)
            # Desbalanceamento: quanto o worker mais lento passa da média
            # (1,0 = perfeitamente balanceado).
            res["desbalanceamento"] = max(calculos) / media if media > 0 else 1.0
        return res

    def imprimir_resumo(self):
        """Mostra o resumo no terminal."""
        res = self.resumo()
        print()
        print("=== ESTATÍSTICAS ===")
        if "pico_espalhadores" in res:
            print(f"Pico de espalhadores: {res['pico_espalhadores']:,} "
                  f"(geração {res['geracao_do_pico']})")
            print(f"Alcance final: {res['alcance_final'] * 100:.2f}% da população")
        for t in self.por_trabalhador:
            print(f"Worker {t['trabalhador']}: cálculo {t['calculo_s']:.4f} s | "
                  f"comunicação {t['comunicacao_s']:.4f} s | espera {t['espera_s']:.4f} s")
        if "desbalanceamento" in res:
            print(f"Desbalanceamento (mais lento / média): {res['desbalanceamento']:.3f}")

    def salvar(self, pasta):
        """Grava geracoes.csv, trabalhadores.csv e resumo.csv em `pasta`."""
        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        prefixo = f"{self.versao}_"
        self._gravar(pasta / f"{prefixo}geracoes.csv", self.geracoes,
                     ["geracao", "ignorantes", "espalhadores", "inativos", "bots"])
        self._gravar(pasta / f"{prefixo}trabalhadores.csv", self.por_trabalhador,
                     ["trabalhador", "calculo_s", "comunicacao_s", "espera_s", "bytes_enviados"])
        p = self.parametros
        linha = {"versao": self.versao, "linhas": p.linhas, "colunas": p.colunas,
                 "geracoes_pedidas": p.geracoes, "geracoes_executadas": len(self.geracoes),
                 "percentual": p.percentual_espalhadores, "limiar": p.limiar,
                 "trabalhadores": self.trabalhadores, "tempo_laco_s": self.tempo_laco,
                 "tempo_total_s": self.tempo_total}
        linha.update(self.resumo())
        self._gravar(pasta / f"{prefixo}resumo.csv", [linha], list(linha))
        return pasta

    @staticmethod
    def _gravar(caminho, linhas, campos):
        """Grava uma lista de dicionários em CSV (UTF-8, newline="" para o Windows)."""
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(linhas)
