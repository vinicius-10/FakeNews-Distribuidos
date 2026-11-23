<#
.SYNOPSIS
    Executa a versão distribuída em 3 máquinas: o coordenador aqui e um worker
    em cada TV box, via SSH.

.DESCRIPTION
    A cadeia de halos exige uma ORDEM de conexão: o rank (e portanto a faixa de
    linhas) é a ordem de chegada no coordenador. Por isso o script NÃO dispara os
    dois SSH de uma vez — ele espera o coordenador anunciar "worker N/M
    conectado" antes de disparar o próximo.

    Antes de começar, o script valida:
      - o firewall local está liberado para o python.exe (perfil da rede atual);
      - os dois nós respondem na porta SSH;
      - o projeto existe nos nós (rode preparar-no-linux.sh primeiro).

.PARAMETER No1
    Usuário@host do primeiro worker (rank 0). Ex.: btv9@192.168.0.8

.PARAMETER No2
    Usuário@host do segundo worker (rank 1). Ex.: btvx@192.168.0.9

.PARAMETER Porta
    Porta do coordenador. Padrão 5000.

.PARAMETER Linhas / Colunas / Geracoes / Limiar
    Cenário da simulação. Padrão 4000x4000, 30 gerações, limiar 2 — grande o
    bastante para a rede física importar no tempo.

.EXAMPLE
    pwsh -File distribuido\rede\rodar-3-maquinas.ps1 `
        -No1 btv9@192.168.0.8 -No2 btvx@192.168.0.9
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$No1,
    [Parameter(Mandatory)][string]$No2,
    [int]$Porta = 5000,
    [int]$Workers = 3,
    [int]$Linhas = 4000,
    [int]$Colunas = 4000,
    [int]$Geracoes = 30,
    [int]$Limiar = 2,
    [switch]$Bits,
    [string]$DiretorioRemoto = '~/FakeNews-Distribuidos'
)

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Saida = Join-Path $Raiz "experimentos\resultados\rede"

function Ciano($t) { Write-Host $t -ForegroundColor Cyan }
function Ok($t)    { Write-Host "  OK   $t" -ForegroundColor Green }
function Falha($t) { Write-Host "  FALHA $t" -ForegroundColor Red }
function Info($t)  { Write-Host "  ...  $t" -ForegroundColor DarkGray }

# ---------------------------------------------------------------------------
# 0. Pré-requisitos
# ---------------------------------------------------------------------------
Ciano "=== 0/4 Pré-requisitos ==="

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Falha "cliente ssh não encontrado. Instale: Get-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0 | Add-WindowsCapability -Online"
    exit 1
}
Ok "cliente ssh disponível"

# Meu IP na rede local (não serve o loopback nem o Tailscale).
$meuIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" } |
    Where-Object { $_.IPAddress -notlike "10.126.*" } |
    Select-Object -First 1).IPAddress
if (-not $meuIp) {
    Falha "não achei o IP da rede local desta máquina"
    exit 1
}
Ok "coordenador vai escutar como $meuIp`:$Porta"

# Firewall: python.exe precisa de regra de ENTRADA no perfil da rede atual,
# senão o box conecta e o handshake do halo morre em silêncio.
$perfilAtual = (Get-NetConnectionProfile |
    Where-Object { $_.InterfaceAlias -eq 'Ethernet' } |
    Select-Object -First 1).NetworkCategory
$regras = Get-NetFirewallRule -Direction Inbound -Action Allow -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match "python" -and $_.Enabled -eq 'True' }
$cobre = $false
foreach ($r in $regras) {
    if ($r.Profile -eq 'Any' -or $r.Profile -match $perfilAtual) { $cobre = $true }
}
if ($cobre) {
    Ok "firewall: python.exe liberado na entrada (perfil $perfilAtual)"
} else {
    Falha "firewall: python.exe NÃO liberado na entrada do perfil '$perfilAtual'."
    Write-Host "         Rode como Administrador:  pwsh -File distribuido\rede\configurar-firewall.ps1" -ForegroundColor Yellow
    exit 1
}

# Nós alcançáveis na porta 22?
foreach ($no in @($No1, $No2)) {
    $hostAlvo = ($no -split '@')[-1]
    Info "testando SSH em $hostAlvo..."
    $teste = Test-NetConnection -ComputerName $hostAlvo -Port 22 -WarningAction SilentlyContinue
    if ($teste.TcpTestSucceeded) {
        Ok "$hostAlvo:22 alcançável"
    } else {
        Falha "$hostAlvo:22 inalcançável — o box está ligado? o SSH está ativo? o IP está certo?"
        exit 1
    }
}

# O projeto está nos nós?
# O PowerShell 5.1 não aceita "&&", "||" nem o "&" de job em segundo plano
# dentro de string interpolada (só existem no PS 7). Por isso o comando remoto é
# montado por concatenação com aspas simples, onde esses caracteres são literais.
foreach ($no in @($No1, $No2)) {
    $testeProj = 'test -f ' + $DiretorioRemoto + '/distribuido/worker.py'
    ssh -o BatchMode=yes -o ConnectTimeout=8 $no $testeProj
    if ($LASTEXITCODE -ne 0) {
        Falha "$no não tem o projeto em $DiretorioRemoto"
        Write-Host "         Rode lá:  ./distribuido/rede/preparar-no-linux.sh --coordenador $meuIp --porta $Porta" -ForegroundColor Yellow
        exit 1
    }
    Ok "$no tem o projeto"
}

# ---------------------------------------------------------------------------
# 1. Coordenador
# ---------------------------------------------------------------------------
Ciano "=== 1/4 Subindo o coordenador ==="
New-Item -ItemType Directory -Force -Path $Saida | Out-Null
$logCoord = Join-Path $Saida "coordenador.log"
if (Test-Path $logCoord) { Remove-Item $logCoord -Force }

$argBits = if ($Bits) { "--bits" } else { "" }
$linha = "python -m distribuido.coordenador --host 0.0.0.0 --porta $Porta --workers $Workers " +
         "--linhas $Linhas --colunas $Colunas --geracoes $Geracoes --limiar $Limiar $argBits"
Info $linha

$coord = Start-Process -FilePath "python" `
    -ArgumentList @("-u", "-m", "distribuido.coordenador", "--host", "0.0.0.0", "--porta", "$Porta",
                    "--workers", "$Workers", "--linhas", "$Linhas", "--colunas", "$Colunas",
                    "--geracoes", "$Geracoes", "--limiar", "$Limiar") + $(if ($Bits) { @("--bits") } else { @() }) `
    -WorkingDirectory $Raiz -RedirectStandardOutput $logCoord -RedirectStandardError "$logCoord.err" `
    -PassThru -NoNewWindow
Ok "coordenador PID $($coord.Id), log em $logCoord"

# Espera um padrão aparecer no log do coordenador (com prazo).
function Esperar-NoLog {
    param([string]$Caminho, [string]$Padrao, [int]$Segundos = 60)
    $limite = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $limite) {
        if ((Test-Path $Caminho) -and (Select-String -Path $Caminho -Pattern $Padrao -Quiet -ErrorAction SilentlyContinue)) {
            return $true
        }
        if ($coord.HasExited) { return $false }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

if (-not (Esperar-NoLog -Caminho $logCoord -Padrao "Aguardando $Workers worker" -Segundos 30)) {
    Falha "o coordenador não subiu. Log:"
    Get-Content $logCoord, "$logCoord.err" -ErrorAction SilentlyContinue | Select-Object -First 20
    if (-not $coord.HasExited) { $coord.Kill() }
    exit 1
}
Ok "coordenador escutando"

# ---------------------------------------------------------------------------
# 2. Workers, um de cada vez (a ordem define o rank)
# ---------------------------------------------------------------------------
# São três nós de processamento em três máquinas:
#   rank 0 = worker LOCAL (esta máquina, ao lado do coordenador)
#   rank 1 = No1
#   rank 2 = No2
# O coordenador soma as contagens; ele não calcula faixa nenhuma.
Ciano "=== 2/4 Disparando os workers (um por vez, em ordem) ==="
$sshJobs = @()
$procsLocais = @()

# rank 0: worker local, conectando no IP de LAN (não em 127.0.0.1) para
# exercitar o mesmo caminho TCP dos outros dois.
$logW0 = Join-Path $Saida "worker-rank0-local.log"
$w0 = Start-Process -FilePath "python" `
    -ArgumentList @("-u", "-m", "distribuido.worker", "--coordenador", "$meuIp`:$Porta",
                    "--escutar", "0.0.0.0") `
    -WorkingDirectory $Raiz -RedirectStandardOutput $logW0 -RedirectStandardError "$logW0.err" `
    -PassThru -NoNewWindow
$procsLocais += $w0
Info "worker rank 0 (local) iniciado, PID $($w0.Id)"
if (-not (Esperar-NoLog -Caminho $logCoord -Padrao "worker 1/$Workers conectado" -Segundos 60)) {
    Falha "o worker local (rank 0) não conectou em 60 s"
    Get-Content $logCoord, "$logCoord.err", $logW0, "$logW0.err" -ErrorAction SilentlyContinue |
        Select-Object -First 20
    if (-not $coord.HasExited) { $coord.Kill() }
    exit 1
}
Ok "worker rank 0 (local) conectado"

$workers = @($No1, $No2)
for ($i = 0; $i -lt $workers.Count; $i++) {
    $rank = $i + 1
    $no = $workers[$i]
    $logRemoto = "/tmp/worker-$rank.log"
    # Comando remoto por concatenação (ver comentário na seção 0): o "&" final do
    # job em segundo plano e o "2>" só são literais em aspas simples.
    $cmd  = 'cd ' + $DiretorioRemoto + '; nohup python3 -u -m distribuido.worker '
    $cmd += '--coordenador ' + $meuIp + ':' + $Porta + ' --escutar 0.0.0.0 '
    $cmd += '> ' + $logRemoto + ' 2> ' + $logRemoto + '.err < /dev/null &'
    Info "iniciando worker rank $rank em $no"
    # O "&" no fim devolve na hora; o SSH fecha e o worker continua via nohup.
    ssh -o BatchMode=yes -o ConnectTimeout=8 $no $cmd
    if ($LASTEXITCODE -ne 0) {
        Falha "ssh para $no falhou (código $LASTEXITCODE)"
        if (-not $coord.HasExited) { $coord.Kill() }
        exit 1
    }
    $sshJobs += [pscustomobject]@{ Rank = $rank; No = $no; Log = $logRemoto }

    # Espera o coordenador confirmar ESTE worker antes de subir o próximo.
    if (-not (Esperar-NoLog -Caminho $logCoord -Padrao "worker $($rank + 1)/$Workers conectado" -Segundos 60)) {
        Falha "o worker rank $rank ($no) não conectou em 60 s. Log do coordenador:"
        Get-Content $logCoord -ErrorAction SilentlyContinue | Select-Object -Last 10
        Falha "log do worker em $no`:$logRemoto"
        if (-not $coord.HasExited) { $coord.Kill() }
        exit 1
    }
    Ok "worker rank $rank ($no) conectado"
}

# ---------------------------------------------------------------------------
# 3. Espera o coordenador terminar
# ---------------------------------------------------------------------------
Ciano "=== 3/4 Aguardando o fim da simulação ==="
$limite = (Get-Date).AddMinutes(15)
while (-not $coord.HasExited -and (Get-Date) -lt $limite) {
    Start-Sleep -Seconds 2
    $ultima = (Get-Content $logCoord -ErrorAction SilentlyContinue | Select-Object -Last 1)
    Write-Host "  $ultima" -ForegroundColor DarkGray
}
if (-not $coord.HasExited) {
    Falha "timeout de 15 min; encerrando o coordenador"
    $coord.Kill()
} else {
    Ok "coordenador terminou"
}

# O worker local (rank 0) termina sozinho quando o coordenador fecha as
# conexões; se algo ficou preso, encerra para não deixar processo órfão.
foreach ($pr in $procsLocais) {
    if ($pr -and -not $pr.HasExited) {
        Info "encerrando worker local Órfão (PID $($pr.Id))"
        $pr.Kill()
    }
}

# ---------------------------------------------------------------------------
# 4. Coleta e comparação
# ---------------------------------------------------------------------------
Ciano "=== 4/4 Resultados ==="
Write-Host ""
Get-Content $logCoord -ErrorAction SilentlyContinue | Select-Object -Last 12

Write-Host ""
Info "logs dos workers:"
foreach ($j in $sshJobs) {
    Write-Host "  --- rank $($j.Rank) · $($j.No) ---" -ForegroundColor DarkGray
    ssh -o BatchMode=yes $j.No "tail -15 $($j.Log) 2>/dev/null" 2>&1 |

        ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
}

Copy-Item $logCoord (Join-Path $Saida "coordenador-3maquinas.log") -Force
Ok "log salvo em $Saida"

Write-Host ""
Ciano "Compare com a sequencial local:"
Write-Host "  python -m sequencial.fakenews_sequencial --linhas $Linhas --colunas $Colunas --geracoes $Geracoes --limiar $Limiar" -ForegroundColor Yellow
Write-Host "  (a contagem final de ignorantes/espalhadores/inativos precisa ser idêntica)" -ForegroundColor Yellow
