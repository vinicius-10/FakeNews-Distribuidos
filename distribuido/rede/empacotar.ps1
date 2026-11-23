<#
.SYNOPSIS
    Gera o ZIP portátil do projeto para copiar aos notebooks do teste.

.DESCRIPTION
    Inclui só o que é necessário para executar as três versões e os testes:
    comum/, sequencial/, paralelo/, distribuido/ (com rede/), testes/,
    experimentos/*.py, README e este guia.

    Fica de fora:
      - .git/            (histórico; os notebooks não precisam)
      - __pycache__/     (bytecode de outra máquina/versão)
      - resultados/      (CSVs e PNGs pesados; cada máquina gera os seus)
      - relatorio/       (LaTeX; não roda nada)

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File distribuido\rede\empacotar.ps1
#>
[CmdletBinding()]
param(
    [string]$Destino = "",
    [string]$VersaoPython = "3.12"
)

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if (-not $Destino) {
    $Destino = Join-Path $PSScriptRoot "FakeNews-distribuido.zip"
}

function Ok($t)    { Write-Host "  OK   $t" -ForegroundColor Green }
function Info($t)  { Write-Host "  ...  $t" -ForegroundColor DarkGray }
function Falha($t) { Write-Host "  FALHA $t" -ForegroundColor Red }

Write-Host "=== Empacotando o projeto para os notebooks ===" -ForegroundColor Cyan
Info "origem : $Raiz"
Info "destino: $Destino"

# Dá para copiar só depois que a suíte passa na versão de Python dos notebooks.
Info "rodando a suíte de testes com Python $VersaoPython antes de empacotar..."
Push-Location $Raiz
# O unittest escreve no stderr; com $ErrorActionPreference = "Stop" o PS 5.1
# trataria isso como erro fatal. Volta para Continue só durante a chamada.
$pausa = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $texto = (& py "-$VersaoPython" -m unittest discover -s testes 2>&1 | Out-String)
    if ($texto -notmatch "Ran \d+ tests" -or $texto -notmatch "OK") {
        Falha "a suíte falhou com Python $VersaoPython; corrija antes de empacotar."
        $texto -split "`n" | Select-Object -Last 20 | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
    $resumo = ($texto -split "`n" | Where-Object { $_ -match "Ran \d+ tests|^OK" }) -join " | "
    Ok $resumo
} finally {
    $ErrorActionPreference = $pausa
    Pop-Location
}

$Estagio = Join-Path $env:TEMP "fakenews-zip-$(Get-Random)"
New-Item -ItemType Directory -Force -Path $Estagio | Out-Null

$incluir = @(
    "comum", "sequencial", "paralelo", "distribuido", "testes",
    "README.md", ".gitignore"
)
foreach ($item in $incluir) {
    $origem = Join-Path $Raiz $item
    if (-not (Test-Path $origem)) { Info "ausente, ignorado: $item"; continue }
    Copy-Item $origem -Destination $Estagio -Recurse -Force
}
Ok "copiados: $($incluir -join ', ')"

# experimentos/: só o código, sem resultados.
$expDst = Join-Path $Estagio "experimentos"
New-Item -ItemType Directory -Force -Path $expDst | Out-Null
Get-ChildItem (Join-Path $Raiz "experimentos") -Filter "*.py" -File -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName -Destination $expDst -Force }
Copy-Item (Join-Path $Raiz "experimentos\README.md") -Destination $expDst -Force -ErrorAction SilentlyContinue
Ok "experimentos: apenas os .py (sem resultados)"

# Limpeza de resíduos que não devem viajar.
Get-ChildItem $Estagio -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force
Get-ChildItem $Estagio -Recurse -File -Include "*.pyc" -ErrorAction SilentlyContinue |
    Remove-Item -Force
Ok "removidos __pycache__ e *.pyc"

# Garante que o guia vai junto.
$guia = Join-Path $Raiz "distribuido\rede\LEIA-ME-3-maquinas.md"
if (Test-Path $guia) {
    Copy-Item $guia -Destination (Join-Path $Estagio "LEIA-ME-3-maquinas.md") -Force
    Ok "guia do teste incluído"
}

# Um marcador da versão, para conferir depois que os notebooks têm o mesmo código.
$commit = (git -C $Raiz rev-parse --short HEAD 2>$null)
$ramo   = (git -C $Raiz rev-parse --abbrev-ref HEAD 2>$null)
@"
Pacote gerado em $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Ramo  : $ramo
Commit: $commit
Python validado: $VersaoPython
Testes: 27 (unittest discover -s testes)
"@ | Set-Content (Join-Path $Estagio "VERSAO.txt") -Encoding UTF8

if (Test-Path $Destino) { Remove-Item $Destino -Force }
Compress-Archive -Path (Join-Path $Estagio "*") -DestinationPath $Destino -CompressionLevel Optimal
$tamanho = [math]::Round((Get-Item $Destino).Length / 1MB, 2)

Remove-Item $Estagio -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Ok "pacote pronto: $Destino ($tamanho MB)"
Write-Host ""
Write-Host "Nos notebooks:" -ForegroundColor Yellow
Write-Host "  1. instale Python $VersaoPython (marque 'Add python.exe to PATH')"
Write-Host "  2. extraia o ZIP, por exemplo em C:\FakeNews-Distribuidos"
Write-Host "  3. cd C:\FakeNews-Distribuidos && python -m unittest discover -s testes"
Write-Host "  4. libere o firewall: powershell -ExecutionPolicy Bypass -File distribuido\rede\configurar-firewall.ps1"
Write-Host "  5. anote o IP com: Get-NetIPAddress -AddressFamily IPv4 | Where-Object { `$_.IPAddress -like '192.168.*' }"
