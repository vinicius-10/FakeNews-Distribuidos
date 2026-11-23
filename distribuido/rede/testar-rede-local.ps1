<#
.SYNOPSIS
    Testa a versão distribuída passando pela INTERFACE DE REDE REAL desta máquina
    (192.168.x.x), em vez de 127.0.0.1.

.DESCRIPTION
    Por que este teste existe
    -------------------------
    `distribuido.executar_local` usa 127.0.0.1. O Windows isenta o loopback do
    filtro de entrada do firewall, então esse teste passa mesmo quando a
    configuração de rede está errada. Ele prova que o protocolo funciona, mas
    NÃO prova que a máquina aceita conexão de outra máquina.

    Aqui o coordenador escuta em 0.0.0.0 e os workers conectam no IP da LAN.
    Assim o caminho TCP é o mesmo de um teste entre máquinas, e erros de
    firewall, bind ou rota aparecem antes de você levar o código para os
    notebooks.

    Os dois workers ainda rodam nesta máquina (a serem substituídos pelos
    notebooks), mas a pilha de rede exercitada é a de produção.

.EXAMPLE
    pwsh -File distribuido\rede\testar-rede-local.ps1
    pwsh -File distribuido\rede\testar-rede-local.ps1 -Linhas 2000 -Colunas 2000
#>
[CmdletBinding()]
param(
    [int]$Porta = 5000,
    [int]$Workers = 2,
    [int]$Linhas = 500,
    [int]$Colunas = 500,
    [int]$Geracoes = 20,
    [int]$Limiar = 2,
    [switch]$Bits
)

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Temp = Join-Path $env:TEMP "fakenews-rede-$(Get-Random)"
New-Item -ItemType Directory -Force -Path $Temp | Out-Null

function Ciano($t) { Write-Host $t -ForegroundColor Cyan }
function Ok($t)    { Write-Host "  OK   $t" -ForegroundColor Green }
function Falha($t) { Write-Host "  FALHA $t" -ForegroundColor Red }
function Info($t)  { Write-Host "  ...  $t" -ForegroundColor DarkGray }

# IP de LAN desta máquina (ignora loopback, link-local e Tailscale).
$ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.*" } |
    Select-Object -First 1).IPAddress
if (-not $ip) {
    Falha "sem IP 192.168.x.x nesta máquina"
    exit 1
}

Ciano "=== Teste de rede real · coordenador em $ip`:$Porta ==="
Info "workers=$Workers  grade=${Linhas}x${Colunas}  geracoes=$Geracoes  limiar=$Limiar  bits=$Bits"

# Porta livre?
$emUso = Get-NetTCPConnection -State Listen -LocalPort $Porta -ErrorAction SilentlyContinue
if ($emUso) {
    Falha "a porta $Porta já está em uso (PID $($emUso.OwningProcess))"
    exit 1
}

$logCoord = Join-Path $Temp "coord.log"
$coordArgs = @("-u", "-m", "distribuido.coordenador", "--host", "0.0.0.0", "--porta", "$Porta",
               "--workers", "$Workers", "--linhas", "$Linhas", "--colunas", "$Colunas",
               "--geracoes", "$Geracoes", "--limiar", "$Limiar")
if ($Bits) { $coordArgs += "--bits" }

$coord = Start-Process -FilePath "python" -ArgumentList $coordArgs -WorkingDirectory $Raiz `
    -RedirectStandardOutput $logCoord -RedirectStandardError "$logCoord.err" `
    -PassThru -NoNewWindow

function EsperarPadrao {
    param([string]$Caminho, [string]$Padrao, [int]$Segundos = 30)
    $limite = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $limite) {
        if ((Test-Path $Caminho) -and (Select-String -Path $Caminho -Pattern $Padrao -Quiet -ErrorAction SilentlyContinue)) { return $true }
        if ($coord.HasExited) { return $false }
        Start-Sleep -Milliseconds 200
    }
    return $false
}

try {
    if (-not (EsperarPadrao $logCoord "Aguardando $Workers worker" 20)) {
        Falha "coordenador não subiu"
        Get-Content $logCoord, "$logCoord.err" -ErrorAction SilentlyContinue | Select-Object -First 15
        exit 1
    }
    Ok "coordenador escutando em 0.0.0.0:$Porta"

    $procs = @()
    for ($i = 0; $i -lt $Workers; $i++) {
        $logW = Join-Path $Temp "worker$i.log"
        $proc = Start-Process -FilePath "python" `
            -ArgumentList @("-u", "-m", "distribuido.worker", "--coordenador", "$ip`:$Porta",
                            "--escutar", "0.0.0.0") `
            -WorkingDirectory $Raiz -RedirectStandardOutput $logW -RedirectStandardError "$logW.err" `
            -PassThru -NoNewWindow
        $procs += $proc
        Info "worker $i iniciado (PID $($proc.Id)), conectando em $ip`:$Porta"
        if (-not (EsperarPadrao $logCoord "worker $($i + 1)/$Workers conectado" 30)) {
            Falha "worker $i não conectou em 30 s"
            Get-Content $logCoord, "$logCoord.err", $logW, "$logW.err" -ErrorAction SilentlyContinue |
                Select-Object -First 25
            exit 1
        }
        Ok "worker $i conectado"
    }

    Ciano "=== Executando ==="
    # `Start-Process -PassThru` no PowerShell 5.1 nem sempre popula ExitCode
    # depois que o processo termina (devolve $null). O sinal confiável de
    # sucesso é o próprio log: a simulação imprime "=== RESULTADO FINAL ===" e
    # qualquer erro deixaria um Traceback / mensagem de erro no stderr.
    $terminou = $coord.WaitForExit(300000)
    if (-not $terminou) { Falha "timeout de 5 min"; $coord.Kill(); exit 1 }
    Start-Sleep -Milliseconds 300

    $textoLog = Get-Content $logCoord -Raw -ErrorAction SilentlyContinue
    $textoErr = Get-Content "$logCoord.err" -Raw -ErrorAction SilentlyContinue
    $temResultado = $textoLog -match "=== RESULTADO FINAL ==="
    $temErro = ($textoErr -match "Traceback|Error|Exception") -or ($textoLog -match "Traceback")

    Write-Host ""
    Get-Content $logCoord | Select-Object -Last 10

    Write-Host ""
    if ($temResultado -and -not $temErro) {
        Ok "teste pela rede real passou"
        Write-Host "  Esta máquina aceita conexões de entrada no IP $ip," -ForegroundColor Green
        Write-Host "  então os notebooks poderão falar com ela quando ligados." -ForegroundColor Green
    } else {
        Falha "a simulação não terminou limpa (resultado=$temResultado, erro=$temErro)"
        Write-Host "  --- stderr ---" -ForegroundColor Yellow
        Get-Content "$logCoord.err" -ErrorAction SilentlyContinue | Select-Object -Last 15
        exit 1
    }
} finally {
    foreach ($pr in $procs) {
        if ($pr -and -not $pr.HasExited) { $pr.Kill() }
    }
    Get-ChildItem $Temp -Filter "*.log*" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  (log: $($_.FullName))" -ForegroundColor DarkGray
    }
}
