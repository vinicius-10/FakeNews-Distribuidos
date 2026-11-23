#!/usr/bin/env bash
# Prepara um notebook com Linux para participar do teste distribuído.
#
# O que faz:
#   1. confere o Python 3 (mínimo 3.8, o projeto usa dataclasses);
#   2. obtém o código do projeto (git clone ou git pull), por padrão da branch main;
#   3. roda a suíte de testes local (prova que o nó está saudável ANTES de entrar
#      na rede — um nó quebrado no meio do teste é muito mais caro de diagnosticar);
#   4. testa se este nó alcança o coordenador e se o próprio nó aceita conexão de
#      entrada, que é o que o vizinho precisa para trocar o halo.
#
# Uso:
#   ./preparar-no-linux.sh --coordenador 192.168.0.4 --porta 5000
#   ./preparar-no-linux.sh --coordenador 192.168.0.4 --porta 5000 --pular-testes
#   ./preparar-no-linux.sh --coordenador 192.168.0.4 --ramo outra-branch   # testar outra branch
#
# Requer: python3, git, curl ou nc (para o teste de porta). Instala com apt se
# estiver em Debian/Ubuntu e tiver sudo sem senha ou pedir a senha.
set -euo pipefail

COORDENADOR=""
PORTA=5000
PULAR_TESTES=0
DIRETORIO="$HOME/FakeNews-Distribuidos"
REPO="${REPO:-https://github.com/vinicius-10/FakeNews-Distribuidos.git}"
# Branch padrão: main (a versão integrada e revisada). Troque com --ramo ou RAMO=...
RAMO="${RAMO:-main}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --coordenador) COORDENADOR="$2"; shift 2 ;;
        --porta)       PORTA="$2";       shift 2 ;;
        --diretorio)   DIRETORIO="$2";   shift 2 ;;
        --repo)        REPO="$2";        shift 2 ;;
        --ramo)        RAMO="$2";        shift 2 ;;
        --pular-testes) PULAR_TESTES=1;  shift   ;;
        -h|--help)      sed -n '2,25p' "$0"; exit 0 ;;
        *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
    esac
done

if [[ -z "$COORDENADOR" ]]; then
    echo "ERRO: informe --coordenador IP (ex.: --coordenador 192.168.0.4)" >&2
    exit 2
fi

verde()  { printf '\033[32m%s\033[0m\n' "$*"; }
amarelo(){ printf '\033[33m%s\033[0m\n' "$*"; }
vermelho(){ printf '\033[31m%s\033[0m\n' "$*"; }
titulo() { printf '\n\033[36m=== %s ===\033[0m\n' "$*"; }

titulo "1/5 Identificação do nó"
echo "host  : $(hostname)"
echo "ip    : $(hostname -I 2>/dev/null | awk '{print $1}')"
echo "so    : $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -a)"
echo "kernel: $(uname -r)"
echo "cpu   : $(nproc) núcleo(s)"
echo "ram   : $(awk '/MemTotal/{printf "%.0f MiB", $2/1024}' /proc/meminfo)"

titulo "2/5 Python 3"
if ! command -v python3 >/dev/null 2>&1; then
    amarelo "python3 ausente; tentando instalar..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq && sudo apt-get install -y python3 python3-venv git
    else
        vermelho "instale python3 e git manualmente e rode de novo"; exit 1
    fi
fi
PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
echo "python3: $PYVER"
python3 - <<'PY'
import sys
if sys.version_info < (3, 8):
    sys.exit("ERRO: é preciso Python 3.8 ou mais novo (o projeto usa dataclasses).")
print("versão OK (>= 3.8)")
PY

titulo "3/5 Código do projeto"
if [[ -d "$DIRETORIO/.git" ]]; then
    echo "repositório já existe em $DIRETORIO; atualizando..."
    git -C "$DIRETORIO" fetch --quiet origin "$RAMO"
    git -C "$DIRETORIO" checkout --quiet "$RAMO"
    git -C "$DIRETORIO" reset --hard --quiet "origin/$RAMO"
else
    echo "clonando $REPO (ramo $RAMO) em $DIRETORIO..."
    git clone --quiet --branch "$RAMO" "$REPO" "$DIRETORIO"
fi
echo "commit: $(git -C "$DIRETORIO" rev-parse --short HEAD) — $(git -C "$DIRETORIO" log -1 --format=%s)"

titulo "4/5 Suíte de testes local"
if [[ "$PULAR_TESTES" -eq 1 ]]; then
    amarelo "pulada (--pular-testes)"
else
    cd "$DIRETORIO"
    # 27 testes; roda em ~5 s no PC e talvez 30-60 s num notebook mais fraco.
    if python3 -m unittest discover -s testes 2>&1 | tail -5; then
        verde "suíte passou neste nó"
    else
        vermelho "a suíte FALHOU neste nó; corrija antes do teste entre máquinas"
        exit 1
    fi
fi

titulo "5/5 Conectividade"
MEU_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "este nó       : $MEU_IP"
echo "coordenador   : $COORDENADOR:$PORTA"

# A) este nó alcança o coordenador?
if python3 - "$COORDENADOR" "$PORTA" <<'PY'
import socket, sys
host, porta = sys.argv[1], int(sys.argv[2])
try:
    with socket.create_connection((host, porta), timeout=5):
        print("  -> OK: coordenador alcançável")
except OSError as e:
    print(f"  -> FALHA ao alcançar o coordenador: {type(e).__name__}: {e}")
    sys.exit(1)
PY
then :; else
    vermelho "o nó não alcança o coordenador. Verifique IP, firewall da máquina do coordenador e se a porta $PORTA está liberada."
    exit 1
fi

# B) este nó aceita conexão de entrada (necessário para o vizinho do halo)?
if python3 - "$MEU_IP" <<'PY'
import socket, sys
host = sys.argv[1]
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind(("0.0.0.0", 0))
srv.listen(1)
porta = srv.getsockname()[1]
try:
    # Tenta conectar pelo próprio IP de LAN, não pelo loopback: o loopback
    # nunca passa pelo firewall e daria um falso positivo.
    cli = socket.create_connection((host, porta), timeout=5)
    cli.close()
    print(f"  -> OK: aceita conexão de entrada em {host}:{porta}")
finally:
    srv.close()
PY
then :; else
    vermelho "o nó NÃO aceita conexão de entrada no IP $MEU_IP. Libere o firewall (ufw/iptables) ou use --escutar na interface certa."
    exit 1
fi

titulo "Pronto"
verde "Nó preparado. Para entrar no teste, rode (aqui mesmo):"
echo ""
echo "  cd $DIRETORIO"
echo "  python3 -m distribuido.worker --coordenador $COORDENADOR:$PORTA --escutar 0.0.0.0"
echo ""
amarelo "Lembre-se: a ORDEM em que os workers conectam define a faixa de cada um."
amarelo "Inicie o worker de um nó, espere o coordenador imprimir \"worker 1/N conectado\","
amarelo "e só então inicie o worker do próximo nó."
