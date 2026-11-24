# Teste da versão distribuída em 3 máquinas

> **Para medir** (bateria com repetições em 4 máquinas, um comando só), use o
> [`ROTEIRO-medicao-4-maquinas.md`](ROTEIRO-medicao-4-maquinas.md). Este guia serve para conferir
> a conexão entre máquinas com uma execução feita à mão.

Guia para rodar a simulação distribuída com o **PC como coordenador** e **um notebook como
worker** de cada lado, na mesma rede local. Tudo aqui foi verificado nesta máquina em
23/nov/2026 (Py 3.11.7 e 3.12.10).

Os scripts desta pasta (`.ps1` no Windows, `.sh` no Linux) são **auxiliares opcionais** para preparar
as máquinas (*firewall*, pacote, testes de rede) e disparar o teste por SSH. A simulação em si roda
igual nos dois sistemas com `python -m distribuido.coordenador` e `python -m distribuido.worker`;
os comandos estão em "Modo manual (quatro terminais)".

## Topologia

```
                    rede da casa 192.168.0.0/24

   PC (192.168.0.4)           NOTEBOOK 1                  NOTEBOOK 2
   ┌──────────────────┐       worker rank 1             worker rank 2
   │ COORDENADOR :5000│       faixa do meio             faixa de baixo
   │ + worker rank 0  │            │                          │
   │   faixa do topo  │            │                          │
   └──────────────────┘            │                          │
        │       └───────────── halo (borda) ──────────────────┘
        │              os workers trocam a borda direto entre si
        └── soma contagens, decide a parada
```

Três máquinas, três workers (`--workers 3`):

| máquina | papel |
|---|---|
| PC | coordenador **e** worker rank 0 |
| notebook 1 | worker rank 1 |
| notebook 2 | worker rank 2 |

- O **rank** (e portanto a faixa de linhas) é a **ordem de chegada** no coordenador. Por isso os
  workers sobem **um de cada vez**, esperando o coordenador imprimir `worker N/3 conectado`.
- As bordas (halo) vão de worker para worker, **sem passar pelo coordenador**. Cada worker abre uma
  porta **aleatória** para o vizinho — é essa porta que exige regra de firewall por *programa*, não
  por número de porta.
- Se preferir **sem** o worker local (só os dois notebooks processando), use `--workers 2`; nesse
  caso não suba o worker no PC.

## Antes de tudo: o firewall (é aqui que 90% dos testes entre máquinas falham)

Descoberta importante nesta máquina: o `python.exe` está liberado no firewall **só no perfil
`Public`**, mas o Ethernet está em **`Private`**. Nesse estado o notebook conecta na porta 5000 e o
handshake do halo **morre em silêncio** — sem mensagem de erro, o worker fica esperando até estourar
o timeout de 600 s.

Confira o perfil da sua rede:

```powershell
Get-NetConnectionProfile | Select-Object InterfaceAlias, NetworkCategory
```

**No PC (coordenador), em um PowerShell como Administrador:**

```powershell
cd C:\Users\rafin\vinicius-10__FakeNews-Distribuidos
powershell -ExecutionPolicy Bypass -File distribuido\rede\configurar-firewall.ps1
```

O script libera o `python.exe` nas conexões de entrada para os perfis `Private`, `Domain` e `Public`,
e no fim mostra o que criou. Para desfazer: `... -Remover`.

**Nos notebooks Windows:** o mesmo procedimento, apontando para a pasta onde o projeto foi copiado.

**Nos notebooks Linux:** se o `ufw` estiver ativo, libere o Python (ou o intervalo usado):

```bash
sudo ufw allow from 192.168.0.0/24 to any port 5000 proto tcp
sudo ufw allow from 192.168.0.0/24 to any app "Python3" 2>/dev/null || \
    sudo ufw allow from 192.168.0.0/24 to any port 1024:65535 proto tcp
```

## Preparar os notebooks

### Windows

1. Instale o **Python 3.12** (marque *Add python.exe to PATH*):
   https://www.python.org/downloads/release/python-31210/
2. Copie o pacote `FakeNews-distribuido.zip` (gerado por `distribuido/rede/empacotar.ps1`) e
   extraia, por exemplo, em `C:\FakeNews-Distribuidos`.
3. Rode a suíte de testes **no notebook**, antes de entrar na rede:

   ```powershell
   cd C:\FakeNews-Distribuidos
   python -m unittest discover -s testes
   ```

   Precisa terminar com `OK` (56 testes). Se falhar aí, não adianta seguir.
4. Libere o firewall (seção anterior).

### Linux

O script `preparar-no-linux.sh` faz tudo (clona a branch `main`, testa, verifica conectividade).
Para testar outra branch, acrescente `--ramo <branch>`:

```bash
./preparar-no-linux.sh --coordenador 192.168.0.4 --porta 5000
```

Se preferir sem git, extraia o ZIP e rode `python3 -m unittest discover -s testes` dentro da pasta.

## Descobrir o IP de cada máquina

```powershell
# Windows
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" } |
    Select-Object IPAddress, InterfaceAlias
```

```bash
# Linux
hostname -I
```

Anote: **PC = 192.168.0.4** (já confirmado). Notebook 1 e Notebook 2 terão os IPs que aparecerem.

## Rodar o teste

### Modo assistido (recomendado): o script faz a ordem certa

No PC, com os dois notebooks preparados e ligados:

```powershell
cd C:\Users\rafin\vinicius-10__FakeNews-Distribuidos
powershell -ExecutionPolicy Bypass -File distribuido\rede\rodar-3-maquinas.ps1 `
    -No1 <usuario>@<ip-notebook1> -No2 <usuario>@<ip-notebook2>
```

O script valida firewall e SSH, sobe o coordenador, dispara cada worker via SSH **esperando a
confirmação** antes do próximo, junta os logs e salva em `experimentos/resultados/rede/`.
Requer OpenSSH Server ativo nos notebooks.

### Modo manual (quatro terminais)

**Terminal 1 — no PC (coordenador):**

```powershell
cd C:\Users\rafin\vinicius-10__FakeNews-Distribuidos
python -m distribuido.coordenador --host 0.0.0.0 --porta 5000 --workers 3 `
    --linhas 4000 --colunas 4000 --geracoes 30 --limiar 2
```

**Terminal 2 — no PC (worker rank 0)** — só depois de ver `Aguardando 3 worker(s)`:

```powershell
cd C:\Users\rafin\vinicius-10__FakeNews-Distribuidos
python -m distribuido.worker --coordenador 192.168.0.4:5000 --escutar 0.0.0.0
```

Espere o coordenador imprimir `worker 1/3 conectado`.

**Terminal 3 — notebook 1 (rank 1):**

```powershell
cd C:\FakeNews-Distribuidos
python -m distribuido.worker --coordenador 192.168.0.4:5000 --escutar 0.0.0.0
```

Espere `worker 2/3 conectado`.

**Terminal 4 — notebook 2 (rank 2):**

```powershell
python -m distribuido.worker --coordenador 192.168.0.4:5000 --escutar 0.0.0.0
```

Espere `worker 3/3 conectado` e a simulação começa sozinha.

> **Atenção ao número de workers:** `--workers 3` exige exatamente 3 workers conectando (1 local +
> 2 notebooks). Faltando um, o coordenador espera até o `--timeout` (600 s). Sobrando, o quarto
> fica de fora.

> **Tempo e conexões estranhas:** o `tempo_total` (linha "Tempo desde a conexão de todos os
> workers") só começa depois que o último worker conecta; o tempo de abrir os terminais não entra.
> Uma conexão que não é de worker na porta do coordenador (ex.: `Test-NetConnection -Port 5000`,
> navegador) é descartada com o aviso `conexão de IP:porta descartada`, sem gastar um rank; a
> que conecta e não fala nada é descartada depois de 10 s.

## Validar o resultado

O teste só vale se a **contagem final for idêntica** à sequencial. Rode no PC:

```powershell
python -m sequencial.fakenews_sequencial --linhas 4000 --colunas 4000 --geracoes 30 --limiar 2
```

Compare os três números (`Ignorantes finais`, `Espalhadores finais`, `Inativos finais`). Têm de ser
iguais aos da distribuída. Nesta máquina, com 500×500 / 20 gerações / limiar 2, os dois deram
`108.188 / 855 / 140.957` — conferido.

### Medir o ganho real de rede

Para o relatório, vale comparar os tempos:

```powershell
# local (loopback, sem latência de rede)
python -m distribuido.executar_local --workers 3 --linhas 4000 --colunas 4000 --limiar 2

# entre máquinas (use --estatisticas para ver comunicação x espera por worker)
python -m distribuido.coordenador --host 0.0.0.0 --workers 3 `
    --linhas 4000 --colunas 4000 --limiar 2 --estatisticas experimentos/resultados/rede
```

O perfil por worker mostra `comunicacao_s` e `bytes_enviados`, e `--bits` reduz o halo de 1 byte para
1 bit por célula (8× menor) — bom argumento para a melhoria 6.

## O que já foi validado nesta máquina (23/nov/2026)

Antes de levar aos notebooks, estes testes passaram aqui:

| Verificação | Como | Resultado |
|---|---|---|
| Suíte de testes, Python 3.11.7 | `python -m unittest discover -s testes` | **27 testes OK** |
| Suíte de testes, Python 3.12.10 | `py -3.12 -m unittest discover -s testes` | **27 testes OK** |
| As 4 versões no cenário padrão | seq / paralela proc / paralela thread / distrib. local | `9.463 / 0 / 537` igual nas quatro |
| Cenário longo (limiar 2, 26 gerações) | seq × distribuída `--bits` | `5.532 / 0 / 4.468` idêntico |
| **Distribuída pela interface de LAN**, 2 workers | `testar-rede-local.ps1` (500×500, 20 ger) | `108.188 / 855 / 140.957` = sequencial |
| **Distribuída pela interface de LAN**, 3 workers | `testar-rede-local.ps1 -Workers 3` (800×800, 25 ger) | `272.616 / 880 / 366.504` = sequencial |
| Pacote portátil é autossuficiente | ZIP extraído em pasta limpa, Py 3.12 | 27 testes OK + distribuída rodando |

O teste "pela interface de LAN" é o que importa: ele usa o IP `192.168.0.4` em vez de `127.0.0.1`,
então passa pelo mesmo caminho TCP de um teste entre máquinas. O loopback do Windows é isento do
filtro de entrada do firewall e daria um falso positivo.

O que **ainda falta** e depende dos notebooks:

- [ ] liberar o firewall no PC (perfil `Private`) — comando na primeira seção;
- [ ] preparar os dois notebooks (Python 3.12 + pacote + suíte OK);
- [ ] rodar com as 3 máquinas de verdade e comparar com a sequencial;
- [ ] medir tempo e preencher a tabela de cenários para o relatório.

## Problemas comuns

| Sintoma | Causa provável | Ação |
|---|---|---|
| `worker N/M conectado` nunca aparece | firewall do coordenador no perfil errado | rode `configurar-firewall.ps1` |
| Worker conecta e trava | firewall do **worker** bloqueando a porta aleatória do halo | libere o `python.exe` também nos notebooks |
| `não foi possível conectar em 30 s` | IP errado ou coordenador ainda não subiu | confira o IP; o worker tenta de novo por 30 s |
| Última linha do PC parada em "Aguardando N" | faltou subir um worker / número de workers errado | `--workers` tem de bater com os workers reais |
| `conexão de IP:porta descartada` | algo que não é worker conectou na porta (teste de porta, navegador) | nada a fazer: o coordenador ignora e continua esperando os workers |
| Resultado diferente da sequencial | não deveria acontecer | rode `python -m unittest discover -s testes`; se passar, anote o cenário e me traga |
| Notebook não acha o PC | redes diferentes (Wi-Fi de visitante, VPN) | desligue VPN; confirme que os dois estão em 192.168.0.0/24 |

## Cenário sugerido para o relatório

Uma bateria que mostra escala real (grade grande o bastante para a rede importar):

| # | Configuração | O que mede |
|---|---|---|
| 1 | sequencial 4000×4000, 30 ger, limiar 2 | referência (T_seq) |
| 2 | distribuída local, 3 workers | melhor caso possível (sem latência) |
| 3 | distribuída real, 3 máquinas | custo real de comunicação |
| 4 | distribuída real, 3 máquinas, `--bits` | ganho da melhoria 6 |

Speedup `S = T_seq / T_dist` e eficiência `E = S / 3`. Repita 3–5 vezes e use a mediana; descarte a
primeira execução (aquecimento de JIT/cache de página).
