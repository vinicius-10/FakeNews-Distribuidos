<#
.SYNOPSIS
    Libera o python.exe nas conexões de ENTRADA do Firewall do Windows.

.DESCRIPTION
    A versão distribuída abre dois tipos de porta de entrada:

      1. o coordenador, em --porta (5000 por padrão);
      2. cada worker, numa porta ALEATÓRIA (porta 0) para o vizinho de cima
         conectar e trocar o halo.

    Como a porta do worker é escolhida pelo sistema a cada execução, não adianta
    liberar a porta 5000: é preciso liberar o PROGRAMA python.exe inteiro nas
    conexões de entrada.

    As regras que já existiam nesta máquina valem só para o perfil "Public"
    (verificado em 23/nov/2026), mas a rede Ethernet da casa está como
    "Private". Sem a regra no perfil correto o Windows descarta os pacotes
    SYN em silêncio: o worker fica esperando a conexão até estourar o timeout
    de 600 s, sem nenhuma mensagem que explique o motivo.

.PARAMETER Remover
    Remove as regras criadas por este script (antes da limpeza).

.EXAMPLE
    # Executar como Administrador
    pwsh -File distribuido\rede\configurar-firewall.ps1
    pwsh -File distribuido\rede\configurar-firewall.ps1 -Remover
#>
[CmdletBinding()]
param([switch]$Remover)

$ErrorActionPreference = "Stop"
$NomeBase = "FakeNews-Distribuida"

# Confere se está elevado: Get-NetFirewallRule funciona, mas New-NetFirewallRule
# falha sem privilégio de administrador.
$ehAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $ehAdmin) {
    Write-Host "ERRO: execute este script em um PowerShell como Administrador." -ForegroundColor Red
    exit 1
}

if ($Remover) {
    $regras = Get-NetFirewallRule -DisplayName "$NomeBase*" -ErrorAction SilentlyContinue
    if ($regras) {
        $regras | Remove-NetFirewallRule
        Write-Host "Removidas $($regras.Count) regra(s) '$NomeBase*'." -ForegroundColor Yellow
    } else {
        Write-Host "Nenhuma regra '$NomeBase*' encontrada." -ForegroundColor Yellow
    }
    exit 0
}

# Todos os interpretadores Python que existirem nesta máquina.
$interpretadores = @()
foreach ($cmd in @("python.exe", "pythonw.exe")) {
    $caminhos = (Get-Command $cmd -All -ErrorAction SilentlyContinue).Source |
        Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
    $interpretadores += $caminhos
}
# Também os Pythons instalados via uv (aparecem nas regras antigas).
$uv = Get-ChildItem "$env:APPDATA\uv\python" -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName "python.exe" } |
    Where-Object { Test-Path $_ }
$interpretadores += $uv
$interpretadores = $interpretadores | Where-Object { $_ } | Select-Object -Unique

if (-not $interpretadores) {
    Write-Host "ERRO: nenhum python.exe encontrado no PATH nem em %APPDATA%\uv\python." -ForegroundColor Red
    exit 1
}

# Perfis que interessam: a rede da casa às vezes é Private, às vezes Public
# (quando o Windows não reconhece o roteador). Cobrir todos evita a surpresa.
$perfis = @("Private", "Domain", "Public")

Write-Host "Interpretadores encontrados:" -ForegroundColor Cyan
$interpretadores | ForEach-Object { Write-Host "  $_" }
Write-Host ""

foreach ($prog in $interpretadores) {
    $sufixo = [System.IO.Path]::GetFileNameWithoutExtension($prog)
    $hash = (Get-FileHash $prog -Algorithm SHA256).Hash.Substring(0, 8)
    $nome = "$NomeBase (entrada TCP) - $sufixo $hash"
    foreach ($perfil in $perfis) {
        $existente = Get-NetFirewallRule -DisplayName $nome -ErrorAction SilentlyContinue |
            Where-Object { $_.Profile -eq $perfil }
        if ($existente) {
            Write-Host "  já existe: $nome [$perfil]" -ForegroundColor DarkGray
            continue
        }
        New-NetFirewallRule -DisplayName $nome -Direction Inbound -Action Allow `
            -Program $prog -Protocol TCP -Profile $perfil -Enabled True | Out-Null
        Write-Host "  criada: $nome [$perfil]" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Perfis de rede ativos ===" -ForegroundColor Cyan
Get-NetConnectionProfile | Select-Object InterfaceAlias, NetworkCategory |
    Format-Table -AutoSize

Write-Host "=== Portas de entrada liberadas para o python ===" -ForegroundColor Cyan
Get-NetFirewallRule -Direction Inbound -Action Allow -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like "$NomeBase*" } |
    Select-Object DisplayName, Profile, Enabled |
    Format-Table -AutoSize
