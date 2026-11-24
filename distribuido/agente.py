"""
Agente da medição em rede: roda em cada máquina e faz o que a medição mandar.

Por que existe
--------------
Numa bateria com repetições, a versão distribuída roda centenas de vezes, e em
cada execução um worker precisa subir em cada máquina, na ordem certa. Fazer
isso à mão não dá. O agente fica ligado durante a bateria inteira e, a cada
pedido de `experimentos/medir_rede.py` (no computador do coordenador):

- `workers`: sobe N workers nesta máquina (`python -m distribuido.worker`, como
  se alguém digitasse), cada um com a sua `--ordem`, espera terminarem e
  responde se deu certo;
- `medir`: roda a sequencial nesta máquina com o `medir.py` (aquecimento +
  repetições) e devolve as medições, que dão a velocidade de cada máquina;
- `fim`: encerra.

O agente é quem conecta no coordenador (conexão de saída), então não precisa de
SSH nem de porta aberta só para ele. Os workers continuam precisando aceitar a
conexão do vizinho (a mesma regra de firewall de sempre). Se a conexão cair, o
agente tenta de novo a cada 5 s: rodar a medição outra vez retoma a bateria.

Uso (em cada máquina, inclusive na do coordenador):
    python -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 0
    python3 -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 3

`--posicao` define a ordem das máquinas (0 = faixa de cima). Na máquina do
coordenador, use o IP da rede local, nunca 127.0.0.1: o endereço por onde o
worker chega é o que o vizinho usa para se conectar a ele.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # permite rodar de qualquer diretório
    sys.path.insert(0, str(RAIZ))

from distribuido import protocolo as p  # noqa: E402

# Espera máxima por um comando: enquanto outra máquina roda a fase 1 (minutos)
# ou enquanto a bateria usa só parte das máquinas, este agente fica parado.
TIMEOUT_COMANDO = 6 * 3600
PAUSA_RECONEXAO = 5.0


# ---------------------------------------------------------------------------
# Dados da máquina (vão para ambiente_maquinas.csv)
# ---------------------------------------------------------------------------

def _dados_windows():
    """Nome da CPU, núcleos físicos e RAM pelo PowerShell (já vem no Windows)."""
    comando = ("$c = Get-CimInstance Win32_Processor; "
               "@{cpu = ($c | Select-Object -First 1).Name; "
               "fisicos = ($c | Measure-Object NumberOfCores -Sum).Sum; "
               "ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory} "
               "| ConvertTo-Json")
    saida = subprocess.run(["powershell", "-NoProfile", "-Command", comando],
                           capture_output=True, text=True, timeout=30).stdout
    dados = json.loads(saida)
    return dados.get("cpu"), dados.get("fisicos"), dados.get("ram")


def _dados_linux():
    """Nome da CPU, núcleos físicos (pares físico/núcleo distintos) e RAM."""
    cpu = None
    nucleos = set()
    fisico = None
    with open("/proc/cpuinfo", encoding="utf-8") as arquivo:
        for linha in arquivo:
            chave, _, valor = linha.partition(":")
            chave, valor = chave.strip(), valor.strip()
            if chave == "model name" and cpu is None:
                cpu = valor
            elif chave == "physical id":
                fisico = valor
            elif chave == "core id":
                nucleos.add((fisico, valor))
    ram = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    return cpu, len(nucleos) or None, ram


def descrever_maquina(cpu=None, fisicos=None, ambiente=None):
    """
    Ambiente desta máquina no mesmo formato do `medir.py`, completado com o nome
    da CPU, os núcleos físicos e a RAM, que a biblioteca padrão não informa.
    Qualquer falha na consulta só deixa o campo vazio: não derruba o agente.
    """
    from experimentos.medir import descrever_ambiente
    info = descrever_ambiente(cpu, fisicos, ambiente or "medição em rede (agente)")
    try:
        if sys.platform.startswith("win"):
            nome, nucleos, ram = _dados_windows()
        elif sys.platform.startswith("linux"):
            nome, nucleos, ram = _dados_linux()
        else:
            nome = nucleos = ram = None
    except (OSError, ValueError, subprocess.SubprocessError):
        nome = nucleos = ram = None
    if nome and not cpu:
        info["processador"] = nome
    if nucleos and info.get("nucleos_fisicos") in ("", None):
        info["nucleos_fisicos"] = nucleos
    if ram and info.get("memoria_gb") in ("", None):
        info["memoria_gb"] = round(int(ram) / 1024 ** 3, 1)
    return info


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

def subir_workers(comando, host_coordenador, escutar):
    """
    Sobe `quantos` workers (subprocessos) e espera todos terminarem.

    Cada um recebe `--ordem ordem_base + i`: as faixas desta máquina ficam
    juntas na cadeia, então só as bordas entre máquinas passam pela rede.
    """
    porta, quantos = int(comando["porta"]), int(comando["quantos"])
    base, timeout = int(comando["ordem_base"]), float(comando["timeout"])
    processos = [subprocess.Popen(
        [sys.executable, "-m", "distribuido.worker",
         "--coordenador", f"{host_coordenador}:{porta}", "--escutar", escutar,
         "--ordem", str(base + i), "--timeout", str(timeout)],
        cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for i in range(quantos)]
    codigos, erros = [], []
    for processo in processos:
        try:
            _, erro = processo.communicate(timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            processo.kill()
            _, erro = processo.communicate()
        codigos.append(processo.returncode)
        if processo.returncode != 0:
            erros.append(erro.decode("utf-8", "replace")[-800:])
    return {"ok": all(c == 0 for c in codigos), "codigos": codigos, "erros": erros}


def medir_sequencial(comando):
    """Roda a sequencial com o `medir.medir` (aquecimento + repetições) e devolve as linhas."""
    from comum.parametros import ParametrosSimulacao
    from experimentos import medir
    base = ParametrosSimulacao(geracoes=int(comando["geracoes"]), limiar=int(comando["limiar"]),
                               percentual_espalhadores=float(comando["percentual"]),
                               semente=int(comando["semente"]))
    plano = medir.montar_plano([int(t) for t in comando["tamanhos"]], [1], ["sequencial"])
    # CSV temporário: o `medir.medir` grava a cada configuração, e o resultado
    # que vale é o que volta para a medição (não suja experimentos/resultados/).
    with tempfile.TemporaryDirectory() as pasta:
        linhas = medir.medir(plano, base, int(comando["repeticoes"]),
                             int(comando["aquecimento"]), float(comando["timeout"]),
                             Path(pasta) / "sequencial.csv")
    esperado = len(plano) * int(comando["repeticoes"])
    return {"ok": len(linhas) == esperado, "linhas": linhas,
            "erros": [] if len(linhas) == esperado else
            [f"{len(linhas)} de {esperado} medições (veja o terminal do agente)"]}


def atender(sock, host_coordenador, escutar):
    """Executa os comandos até chegar `fim` (devolve True) ou a conexão cair (exceção)."""
    while True:
        _, comando = p.receber_json(sock, p.COMANDO)
        acao = comando.get("acao")
        if acao == "fim":
            return True
        try:
            if acao == "workers":
                resposta = subir_workers(comando, host_coordenador, escutar)
            elif acao == "medir":
                print(f"Medindo a sequencial: {comando['tamanhos']}", flush=True)
                resposta = medir_sequencial(comando)
            else:
                resposta = {"ok": False, "erros": [f"ação desconhecida: {acao!r}"]}
        except Exception as erro:  # noqa: BLE001 - o erro vai para a medição, que decide
            resposta = {"ok": False, "erros": [f"{type(erro).__name__}: {erro}"]}
        p.enviar_json(sock, p.RESPOSTA, resposta)


def executar_agente(host, porta, escutar, nome, posicao, ambiente):
    """Conecta, apresenta a máquina e atende os comandos; reconecta se cair."""
    while True:
        try:
            sock = p.conectar(host, porta, TIMEOUT_COMANDO, espera_maxima=30)
        except ConnectionError:
            print(f"Coordenador {host}:{porta} ainda não respondeu; tentando de novo...",
                  flush=True)
            continue
        try:
            p.enviar_json(sock, p.AGENTE, {"nome": nome, "posicao": posicao,
                                           "ambiente": ambiente})
            print(f"Conectado a {host}:{porta} como '{nome}' (posição {posicao}). "
                  "Aguardando comandos...", flush=True)
            if atender(sock, host, escutar):
                print("Medição encerrada pelo coordenador.", flush=True)
                return 0
        except (OSError, ValueError, p.ErroProtocolo) as erro:
            print(f"Conexão com o coordenador perdida ({type(erro).__name__}: {erro}); "
                  f"tentando de novo em {PAUSA_RECONEXAO:.0f} s.", flush=True)
            time.sleep(PAUSA_RECONEXAO)
        finally:
            sock.close()


def main(argv=None):
    """Lê os argumentos e liga o agente."""
    for fluxo in (sys.stdout, sys.stderr):  # acento fora do cp1252 não derruba o agente
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Agente da medição em rede (uma por máquina)")
    parser.add_argument("--coordenador", required=True, metavar="HOST:PORTA",
                        help="IP de rede local da máquina que roda experimentos.medir_rede")
    parser.add_argument("--posicao", type=int,
                        help="ordem da máquina na cadeia (0 = faixa de cima)")
    parser.add_argument("--nome", default=platform.node(), help="nome da máquina nos CSVs")
    parser.add_argument("--escutar", default="0.0.0.0",
                        help="endereço em que os workers esperam o vizinho")
    parser.add_argument("--cpu", help="nome do processador, se a detecção falhar")
    parser.add_argument("--nucleos-fisicos", type=int)
    parser.add_argument("--ambiente", help="condição da medição (ex.: 'na tomada; cabo')")
    args = parser.parse_args(argv)
    if args.posicao is not None and args.posicao < 0:
        parser.error("--posicao não pode ser negativa")
    host, _, porta = args.coordenador.rpartition(":")
    if host in ("127.0.0.1", "localhost"):
        print("Aviso: com 127.0.0.1 esta máquina só funciona se TODAS estiverem nela. "
              "Entre máquinas, use o IP da rede local.", flush=True)
    ambiente = descrever_maquina(args.cpu, args.nucleos_fisicos, args.ambiente)
    print(f"Máquina: {ambiente.get('processador')} | {ambiente.get('sistema')} | "
          f"Python {ambiente.get('python')}", flush=True)
    try:
        return executar_agente(host, int(porta), args.escutar, args.nome, args.posicao,
                               ambiente)
    except KeyboardInterrupt:
        print("\nAgente interrompido.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
