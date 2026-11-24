"""
Medição da versão distribuída numa rede real, com um comando só.

Como funciona
-------------
Cada máquina roda `python -m distribuido.agente --coordenador IP:5000 --posicao N`
e deixa ligado. Este script, na máquina do coordenador, espera os agentes e roda
a bateria inteira sozinho, em três fases:

1. **Sequencial em cada máquina** (todas ao mesmo tempo, uma não atrapalha a
   outra): dá o tempo T1 de cada máquina, isto é, a velocidade de cada uma, e
   confere que todas (Windows e Linux) chegam à mesma grade.
2. **Distribuída na rede**: varia o número de máquinas (hosts) e de workers por
   máquina, com e sem `--bits`. Uma configuração por vez, com aquecimento e
   repetições. As h primeiras máquinas (pela posição) entram quando há h hosts.
3. **Parâmetros** na configuração cheia: gerações, percentual e limiar.

Cada execução da fase 2 e 3 grava uma linha com o SHA-256 da grade final e a
coluna `confere`, que compara esse hash com o da sequencial no mesmo cenário.

O que entra no tempo
--------------------
Igual ao `medir.py`: `tempo_laco_s` é só o laço de gerações. A subida dos
workers, as conexões e o envio da grade inicial ficam de fora
(`tempo_total_s` inclui a distribuição da grade e a coleta do resultado).

Retomada
--------
Os CSVs são regravados ao fim de cada configuração. Rodar o mesmo comando de
novo pula o que já foi medido; os agentes reconectam sozinhos.

Uso
---
    python -m experimentos.medir_rede --maquinas 4 --simular     # só a estimativa
    python -m experimentos.medir_rede --maquinas 4 --rede "Wi-Fi"
    python -m experimentos.medir_rede --maquinas 4 --fases 2 3   # pula a fase 1

Saída em `experimentos/resultados/rede/`: `medicoes.csv` (fases 2 e 3),
`sequencial_maquinas.csv` (fase 1) e `ambiente_maquinas.csv`.
"""

import argparse
import csv
import ipaddress
import statistics
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # permite rodar de qualquer diretório
    sys.path.insert(0, str(RAIZ))

from comum.parametros import ParametrosSimulacao  # noqa: E402
from distribuido import coordenador  # noqa: E402
from distribuido import protocolo as p  # noqa: E402
from experimentos import medir  # noqa: E402
from sequencial.fakenews_sequencial import executar_simulacao as executar_sequencial  # noqa: E402

PASTA_PADRAO = RAIZ / "experimentos" / "resultados" / "rede"

# Colunas: as do medir.py (analisar.py continua servindo) + as da rede.
CAMPOS_REDE = medir.CAMPOS + ["fase", "hosts", "workers_por_host", "maquinas", "confere",
                              "rede", "data_hora"]
CAMPOS_FASE1 = ["maquina", "posicao"] + medir.CAMPOS + ["data_hora"]

# Perfis da bateria. `rede` é o do dia do teste (~40 min com 4 máquinas, ver
# --simular); `fumaca` é minúsculo, usado pelos testes automáticos.
PERFIS = {
    "rede": {
        "geracoes": 20, "limiar": 2, "percentual": 0.05, "semente": 42, "aquecimento": 1,
        # Fase 1: cada lote é um comando para o agente.
        "fase1": [{"tamanhos": [1000, 2000], "repeticoes": 5},
                  {"tamanhos": [4000], "repeticoes": 3}],
        # Fase 2: {tamanho: repetições}.
        "escala": {1000: 5, 2000: 3},       # 1..H hosts
        "cheia": {4000: 3},                 # só com todos os hosts
        "bits": {2000: 3},                  # --bits, só com todos os hosts
        "workers_por_host": [1, 2, 4],
        # Fase 3: todos os hosts × `workers_por_host` workers em cada um.
        "fase3": {"tamanho": 1000, "workers_por_host": 2, "repeticoes": 3,
                  "geracoes": [10, 20, 40], "percentuais": [0.01, 0.05, 0.10],
                  "limiares": [1, 2, 3]},
    },
    "fumaca": {
        "geracoes": 4, "limiar": 2, "percentual": 0.1, "semente": 42, "aquecimento": 0,
        "fase1": [{"tamanhos": [24, 40], "repeticoes": 1}],
        "escala": {24: 1, 40: 1},
        "cheia": {48: 1},                   # sem fase 1: a referência é calculada aqui
        "bits": {40: 1},
        "workers_por_host": [1, 2],
        "fase3": {"tamanho": 24, "workers_por_host": 1, "repeticoes": 1,
                  "geracoes": [2, 6], "percentuais": [0.05, 0.1], "limiares": [2]},
    },
}

# Estimativa: segundos por célula por geração na máquina mais lenta (o i9 do
# grupo faz ~0,35 µs) e custo fixo de cada execução distribuída (subir os
# workers com Python, conectar, enviar a grade).
CUSTO_CELULA_PADRAO = 0.5e-6
SOBRECARGA_EXECUCAO = 1.5


# ---------------------------------------------------------------------------
# Plano
# ---------------------------------------------------------------------------

def montar_plano(perfil, maquinas):
    """Lista de lotes da fase 1 e de configurações das fases 2 e 3."""
    cfg = PERFIS[perfil]
    comum = {"geracoes": cfg["geracoes"], "limiar": cfg["limiar"],
             "percentual": cfg["percentual"]}

    def config(fase, tamanho, hosts, wph, bits, repeticoes, **extra):
        return {"fase": fase, "linhas": tamanho, "hosts": hosts, "workers_por_host": wph,
                "bits": bits, "repeticoes": repeticoes, **{**comum, **extra}}

    rede = []
    for tamanho, reps in cfg["escala"].items():
        for hosts in range(1, maquinas + 1):
            for wph in cfg["workers_por_host"]:
                rede.append(config(2, tamanho, hosts, wph, False, reps))
    for tamanho, reps in cfg["cheia"].items():
        for wph in cfg["workers_por_host"]:
            rede.append(config(2, tamanho, maquinas, wph, False, reps))
    for tamanho, reps in cfg["bits"].items():
        for wph in cfg["workers_por_host"]:
            rede.append(config(2, tamanho, maquinas, wph, True, reps))

    f3 = cfg["fase3"]
    cenarios = [(g, cfg["percentual"], cfg["limiar"]) for g in f3["geracoes"]]
    cenarios += [(cfg["geracoes"], pct, lim) for pct in f3["percentuais"]
                 for lim in f3["limiares"]]
    vistos = set()
    for geracoes, pct, lim in cenarios:
        if (geracoes, pct, lim) in vistos:
            continue
        vistos.add((geracoes, pct, lim))
        rede.append(config(3, f3["tamanho"], maquinas, f3["workers_por_host"], False,
                           f3["repeticoes"], geracoes=geracoes, percentual=pct, limiar=lim))

    for item in rede:
        if item["hosts"] * item["workers_por_host"] > item["linhas"]:
            raise ValueError(f"mais workers que linhas em {item}")
    return {"perfil": perfil, "semente": cfg["semente"], "aquecimento": cfg["aquecimento"],
            "comum": comum, "fase1": cfg["fase1"], "rede": rede}


def _num(valor):
    """Normaliza número (int, float ou texto do CSV) para comparar chaves."""
    return f"{float(valor):g}"


def chave_config(config):
    versao = "distribuida_rede_bits" if config["bits"] else "distribuida_rede"
    return (str(config["fase"]), versao, _num(config["linhas"]), _num(config["hosts"]),
            _num(config["workers_por_host"]), _num(config["geracoes"]),
            _num(config["limiar"]), _num(config["percentual"]))


def chave_linha(linha):
    return (str(linha["fase"]), linha["versao"], _num(linha["linhas"]), _num(linha["hosts"]),
            _num(linha["workers_por_host"]), _num(linha["geracoes_pedidas"]),
            _num(linha["limiar"]), _num(linha["percentual"]))


def linha_de_exemplo(config, repeticao):
    """Linha mínima com as colunas que a retomada usa (para testes)."""
    return {"fase": config["fase"],
            "versao": "distribuida_rede_bits" if config["bits"] else "distribuida_rede",
            "linhas": config["linhas"], "hosts": config["hosts"],
            "workers_por_host": config["workers_por_host"],
            "geracoes_pedidas": config["geracoes"], "limiar": config["limiar"],
            "percentual": config["percentual"], "repeticao": repeticao}


def pendentes_rede(configs, linhas_existentes):
    """Configurações que ainda não têm todas as repetições no CSV."""
    contagem = {}
    for linha in linhas_existentes:
        contagem[chave_linha(linha)] = contagem.get(chave_linha(linha), 0) + 1
    return [c for c in configs if contagem.get(chave_config(c), 0) < c["repeticoes"]]


def estimar(plano, maquinas, custo_celula):
    """Estimativa grosseira em segundos de cada fase."""
    aq = plano["aquecimento"]
    g = plano["comum"]["geracoes"]
    fase1 = sum((aq + lote["repeticoes"]) * t * t * g * custo_celula
                for lote in plano["fase1"] for t in lote["tamanhos"])
    fase2 = fase3 = 0.0
    for c in plano["rede"]:
        workers = c["hosts"] * c["workers_por_host"]
        por_execucao = (c["linhas"] ** 2 * c["geracoes"] * custo_celula / workers
                        + SOBRECARGA_EXECUCAO)
        total = (aq + c["repeticoes"]) * por_execucao
        if c["fase"] == 2:
            fase2 += total
        else:
            # + a sequencial de referência, calculada aqui uma vez por cenário.
            fase3 += total + c["linhas"] ** 2 * c["geracoes"] * custo_celula
    return {"fase 1": fase1, "fase 2": fase2, "fase 3": fase3}


def custo_da_fase1(linhas_fase1):
    """Custo por célula da máquina mais lenta, a partir da fase 1 já medida."""
    por_maquina = {}
    for linha in linhas_fase1:
        celulas = float(linha["linhas"]) * float(linha["colunas"])
        geracoes = max(1.0, float(linha["geracoes_executadas"]))
        por_maquina.setdefault(linha["maquina"], []).append(
            float(linha["tempo_laco_s"]) / (celulas * geracoes))
    if not por_maquina:
        return None
    return max(statistics.median(v) for v in por_maquina.values())


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def ler_csv(caminho):
    if not Path(caminho).exists():
        return []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def gravar_csv(caminho, campos, linhas):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)


def agora():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Agentes
# ---------------------------------------------------------------------------

@dataclass
class Agente:
    nome: str
    posicao: object
    ip: str
    ambiente: dict
    sock: object


def aceitar_agentes(servidor, quantidade, espera):
    """Espera `quantidade` agentes e devolve-os ordenados pela posição."""
    servidor.settimeout(espera)
    agentes = []
    print(f"Aguardando {quantidade} agente(s) em "
          f"{servidor.getsockname()[0]}:{servidor.getsockname()[1]}...", flush=True)
    while len(agentes) < quantidade:
        conexao, (ip, porta) = servidor.accept()
        try:
            p.configurar(conexao, p.TIMEOUT_OLA)
            _, dados = p.receber_json(conexao, p.AGENTE)
            nome = str(dados["nome"])
            posicao = dados.get("posicao")
            ambiente = dict(dados.get("ambiente") or {})
        except (OSError, ValueError, KeyError, TypeError, p.ErroProtocolo) as erro:
            conexao.close()
            print(f"  conexão de {ip}:{porta} descartada (não é um agente: {erro})",
                  flush=True)
            continue
        if any(a.nome == nome for a in agentes):
            conexao.close()
            print(f"  agente '{nome}' repetido ({ip}) descartado: use --nome diferente",
                  flush=True)
            continue
        agentes.append(Agente(nome, posicao, ip, ambiente, conexao))
        print(f"  máquina {len(agentes)}/{quantidade}: {nome} ({ip}), posição {posicao}, "
              f"{ambiente.get('processador', '?')}", flush=True)
    agentes.sort(key=lambda a: (a.posicao is None, a.posicao or 0))
    # Um agente em 127.0.0.1 junto com outros de fora quebraria a troca de bordas:
    # o vizinho receberia 127.0.0.1 como endereço e conectaria na própria máquina.
    locais = [a.nome for a in agentes if ipaddress.ip_address(a.ip).is_loopback]
    if locais and len(locais) < len(agentes):
        for agente in agentes:
            agente.sock.close()
        raise RuntimeError(f"agente(s) {locais} conectaram por 127.0.0.1, mas há máquinas de "
                           "fora: rode o agente com --coordenador <IP da rede local>:PORTA")
    return agentes


def _resposta(agente, timeout):
    agente.sock.settimeout(timeout)
    _, resposta = p.receber_json(agente.sock, p.RESPOSTA)
    return resposta


# ---------------------------------------------------------------------------
# Fases
# ---------------------------------------------------------------------------

def fase1(agentes, plano, existentes, caminho, timeout):
    """Sequencial em todas as máquinas ao mesmo tempo; devolve todas as linhas."""
    linhas = list(existentes)
    feitas = {}
    for linha in existentes:
        chave = (linha["maquina"], _num(linha["linhas"]))
        feitas[chave] = feitas.get(chave, 0) + 1
    trava = threading.Lock()
    falhas = []

    def rodar(agente):
        for lote in plano["fase1"]:
            tamanhos = [t for t in lote["tamanhos"]
                        if feitas.get((agente.nome, _num(t)), 0) < lote["repeticoes"]]
            if not tamanhos:
                continue
            try:
                p.enviar_json(agente.sock, p.COMANDO, {
                    "acao": "medir", "tamanhos": tamanhos, "repeticoes": lote["repeticoes"],
                    "aquecimento": plano["aquecimento"], "semente": plano["semente"],
                    "timeout": timeout, **plano["comum"]})
                resposta = _resposta(agente, 4 * 3600)
            except (OSError, ValueError, p.ErroProtocolo) as erro:
                falhas.append(f"{agente.nome}: conexão perdida ({erro})")
                return
            with trava:
                # Linhas antigas destes tamanhos (de uma execução interrompida) saem
                # antes de entrarem as novas: nada fica duplicado.
                refeitos = {_num(t) for t in tamanhos}
                linhas[:] = [l for l in linhas if not (l["maquina"] == agente.nome
                                                       and _num(l["linhas"]) in refeitos)]
                for linha in resposta.get("linhas", []):
                    linhas.append({**linha, "maquina": agente.nome,
                                   "posicao": agente.posicao, "data_hora": agora()})
                gravar_csv(caminho, CAMPOS_FASE1, linhas)
            print(f"  fase 1: {agente.nome} terminou {tamanhos}", flush=True)
            if not resposta.get("ok"):
                falhas.append(f"{agente.nome}: {resposta.get('erros')}")

    threads = [threading.Thread(target=rodar, args=(a,), daemon=True) for a in agentes]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if falhas:
        raise RuntimeError("fase 1 falhou: " + "; ".join(falhas))
    return linhas


def referencias_da_fase1(linhas_fase1):
    """Hash da sequencial por cenário; avisa se as máquinas discordarem."""
    hashes = {}
    for linha in linhas_fase1:
        chave = (_num(linha["linhas"]), _num(linha["geracoes_pedidas"]),
                 _num(linha["limiar"]), _num(linha["percentual"]))
        hashes.setdefault(chave, set()).add(linha["hash_grade"])
    referencias = {}
    for chave, conjunto in hashes.items():
        if len(conjunto) > 1:
            print(f"ALERTA: as máquinas deram grades diferentes na sequencial {chave}", flush=True)
        referencias[chave] = sorted(conjunto)[0]
    return referencias


def _parametros(config, semente):
    return ParametrosSimulacao(linhas=config["linhas"], colunas=config["linhas"],
                               geracoes=config["geracoes"], limiar=config["limiar"],
                               percentual_espalhadores=config["percentual"], semente=semente)


def referencia(config, referencias, semente):
    """Hash da sequencial no cenário da configuração (calcula aqui se faltar)."""
    chave = (_num(config["linhas"]), _num(config["geracoes"]), _num(config["limiar"]),
             _num(config["percentual"]))
    if chave not in referencias:
        print(f"  calculando a sequencial de referência {chave}...", flush=True)
        resultado = executar_sequencial(_parametros(config, semente), mostrar=False)
        referencias[chave] = medir._resumir(resultado, resultado["tempo_total"])["hash_grade"]
    return referencias[chave]


def executar_uma(config, agentes, host, semente, timeout):
    """Uma execução distribuída: os agentes sobem os workers, este processo coordena."""
    hosts, wph = config["hosts"], config["workers_por_host"]
    usados = agentes[:hosts]
    servidor = p.criar_servidor(host, 0)
    porta = servidor.getsockname()[1]
    comandados = []
    erro_execucao = None
    resultado = None
    try:
        for indice, agente in enumerate(usados):
            p.enviar_json(agente.sock, p.COMANDO, {
                "acao": "workers", "porta": porta, "quantos": wph,
                "ordem_base": indice * wph, "timeout": timeout})
            comandados.append(agente)
        resultado = coordenador.executar_coordenador(
            _parametros(config, semente), servidor, hosts * wph, config["bits"],
            mostrar=False, timeout=timeout)
    except (OSError, p.ErroProtocolo) as erro:
        erro_execucao = erro
    finally:
        servidor.close()
    # Toda resposta é lida, mesmo com erro: senão o canal fica fora de sincronia.
    erros = []
    for agente in comandados:
        resposta = _resposta(agente, timeout + 120)
        if not resposta.get("ok"):
            erros.append(f"{agente.nome}: {resposta.get('erros')}")
    if erro_execucao is not None or erros:
        raise RuntimeError(f"{erro_execucao or ''} {'; '.join(erros)}".strip())
    return medir._resumir(resultado, resultado["tempo_total"])


def fases_rede(agentes, configs, plano, referencias, existentes, caminho, rede, host, timeout):
    """Fases 2 e 3: uma configuração por vez, com aquecimento e repetições."""
    linhas = list(existentes)
    pendentes = pendentes_rede(configs, existentes)
    total = len(pendentes)
    for indice, config in enumerate(pendentes, start=1):
        versao = "distribuida_rede_bits" if config["bits"] else "distribuida_rede"
        maquinas = ";".join(a.nome for a in agentes[:config["hosts"]])
        rotulo = (f"[{indice}/{total}] fase {config['fase']} {versao:<21} "
                  f"{config['linhas']}² hosts={config['hosts']} "
                  f"w/host={config['workers_por_host']} g={config['geracoes']} "
                  f"lim={config['limiar']} pct={config['percentual']}")
        print(f"{rotulo} ... ", end="", flush=True)
        esperado = referencia(config, referencias, plano["semente"])
        # Repetições incompletas de uma interrupção anterior são refeitas inteiras.
        linhas = [l for l in linhas if chave_linha(l) != chave_config(config)]
        novas = []
        try:
            for _ in range(plano["aquecimento"]):
                executar_uma(config, agentes, host, plano["semente"], timeout)
            for repeticao in range(1, config["repeticoes"] + 1):
                medida = executar_uma(config, agentes, host, plano["semente"], timeout)
                novas.append({
                    "versao": versao, "modo": "bits" if config["bits"] else "rede",
                    "workers": config["hosts"] * config["workers_por_host"],
                    "linhas": config["linhas"], "colunas": config["linhas"],
                    "geracoes_pedidas": config["geracoes"], "limiar": config["limiar"],
                    "percentual": config["percentual"], "repeticao": repeticao, **medida,
                    "fase": config["fase"], "hosts": config["hosts"],
                    "workers_por_host": config["workers_por_host"], "maquinas": maquinas,
                    "confere": "sim" if medida["hash_grade"] == esperado else "NAO",
                    "rede": rede, "data_hora": agora()})
        except RuntimeError as erro:
            print(f"FALHOU ({erro})", flush=True)
            continue
        linhas.extend(novas)
        gravar_csv(caminho, CAMPOS_REDE, linhas)
        mediana = statistics.median(l["tempo_laco_s"] for l in novas)
        aviso = "" if all(l["confere"] == "sim" for l in novas) else "  <<< GRADE DIFERENTE"
        print(f"mediana {mediana:.3f} s{aviso}", flush=True)
    return linhas


# ---------------------------------------------------------------------------
# Bateria
# ---------------------------------------------------------------------------

def executar_bateria(servidor, maquinas, perfil="rede", pasta=PASTA_PADRAO, rede="",
                     timeout=600.0, fases=(1, 2, 3), espera_agentes=1800.0):
    """Roda a bateria com os agentes que conectarem em `servidor`."""
    pasta = Path(pasta)
    plano = montar_plano(perfil, maquinas)
    caminho_fase1 = pasta / "sequencial_maquinas.csv"
    caminho_rede = pasta / "medicoes.csv"
    host = servidor.getsockname()[0]
    comeco = time.perf_counter()

    agentes = aceitar_agentes(servidor, maquinas, espera_agentes)
    try:
        gravar_csv(pasta / "ambiente_maquinas.csv",
                   ["posicao", "maquina", "ip"] + sorted({k for a in agentes for k in a.ambiente}),
                   [{"posicao": a.posicao, "maquina": a.nome, "ip": a.ip, **a.ambiente}
                    for a in agentes])
        print("Ordem das faixas (de cima para baixo): "
              + " > ".join(a.nome for a in agentes), flush=True)

        linhas_fase1 = ler_csv(caminho_fase1)
        if 1 in fases:
            print("\n=== Fase 1: sequencial em cada máquina (todas ao mesmo tempo) ===",
                  flush=True)
            linhas_fase1 = fase1(agentes, plano, linhas_fase1, caminho_fase1, timeout)
        referencias = referencias_da_fase1(linhas_fase1)

        existentes = ler_csv(caminho_rede)
        for fase in (2, 3):
            if fase not in fases:
                continue
            print(f"\n=== Fase {fase}: distribuída na rede ===", flush=True)
            configs = [c for c in plano["rede"] if c["fase"] == fase]
            existentes = fases_rede(agentes, configs, plano, referencias, existentes,
                                    caminho_rede, rede, host, timeout)
    finally:
        for agente in agentes:
            try:
                p.enviar_json(agente.sock, p.COMANDO, {"acao": "fim"})
            except OSError:
                pass
            agente.sock.close()
    print(f"\nBateria terminada em {(time.perf_counter() - comeco) / 60:.1f} min. "
          f"Resultados em {pasta}", flush=True)


def main(argv=None):
    """Lê os argumentos, mostra a estimativa e roda a bateria."""
    medir._console_seguro()
    parser = argparse.ArgumentParser(
        description="Mede a versão distribuída em várias máquinas (com os agentes ligados)")
    parser.add_argument("--maquinas", type=int, required=True,
                        help="número de máquinas com o agente ligado (inclusive esta)")
    parser.add_argument("--host", default="0.0.0.0", help="endereço de escuta")
    parser.add_argument("--porta", type=int, default=5000, help="porta dos agentes")
    parser.add_argument("--perfil", choices=sorted(PERFIS), default="rede")
    parser.add_argument("--fases", type=int, nargs="+", choices=[1, 2, 3], default=[1, 2, 3])
    parser.add_argument("--rede", default="",
                        help="tipo de rede, gravado no CSV (ex.: 'Wi-Fi', 'cabo')")
    parser.add_argument("--saida", default=str(PASTA_PADRAO), help="pasta dos CSVs")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--espera-agentes", type=float, default=1800.0,
                        help="segundos esperando os agentes conectarem")
    parser.add_argument("--simular", action="store_true",
                        help="só mostra o plano e a estimativa de tempo")
    args = parser.parse_args(argv)
    if args.maquinas < 1:
        parser.error("--maquinas precisa ser pelo menos 1")

    plano = montar_plano(args.perfil, args.maquinas)
    custo = custo_da_fase1(ler_csv(Path(args.saida) / "sequencial_maquinas.csv"))
    origem = "medido na fase 1" if custo else "suposto"
    custo = custo or CUSTO_CELULA_PADRAO
    estimativa = estimar(plano, args.maquinas, custo)
    pendentes = pendentes_rede(plano["rede"], ler_csv(Path(args.saida) / "medicoes.csv"))
    print(f"=== MEDIÇÃO EM REDE ({args.maquinas} máquinas, perfil {args.perfil}) ===")
    print(f"Fase 1: {sum(len(l['tamanhos']) for l in plano['fase1'])} tamanhos por máquina | "
          f"fases 2 e 3: {len(plano['rede'])} configurações ({len(pendentes)} pendentes)")
    print(f"Custo por célula·geração: {custo * 1e6:.2f} µs ({origem}, máquina mais lenta)")
    for fase, segundos in estimativa.items():
        if int(fase[-1]) in args.fases:
            print(f"  {fase}: ~{segundos / 60:.0f} min")
    total = sum(s for f, s in estimativa.items() if int(f[-1]) in args.fases)
    print(f"  total: ~{total / 60:.0f} min (sem descontar o que já foi medido)")
    if args.simular:
        return 0

    servidor = p.criar_servidor(args.host, args.porta)
    try:
        executar_bateria(servidor, args.maquinas, args.perfil, args.saida, args.rede,
                         args.timeout, tuple(args.fases), args.espera_agentes)
    except KeyboardInterrupt:
        print("\nInterrompido. Rode o mesmo comando para continuar de onde parou.")
        return 1
    except (OSError, p.ErroProtocolo, RuntimeError) as erro:
        print(f"\nA bateria parou: {type(erro).__name__}: {erro}\n"
              "Confira se os agentes continuam ligados e rode o mesmo comando: "
              "o que já foi medido é pulado.")
        return 1
    finally:
        servidor.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
