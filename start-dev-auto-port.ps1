param(
    [int]$BackendStartPort = 8080,
    [int]$BackendEndPort = 8090,
    [int]$FrontendStartPort = 3000,
    [int]$FrontendEndPort = 3010,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Test-PortInUse {
    param([int]$Port)
    try {
        return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    } catch {
        return $false
    }
}

function Get-FreePort {
    param(
        [int]$From,
        [int]$To
    )

    for ($p = $From; $p -le $To; $p++) {
        if (-not (Test-PortInUse -Port $p)) {
            return $p
        }
    }

    return $null
}

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $rootDir 'smart-summary'
$frontendDir = Join-Path $rootDir 'smart-summary-web'

$backendPort = Get-FreePort -From $BackendStartPort -To $BackendEndPort
if ($null -eq $backendPort) {
    Write-Host "No free backend port found in range $BackendStartPort-$BackendEndPort." -ForegroundColor Red
    exit 1
}

$frontendPort = Get-FreePort -From $FrontendStartPort -To $FrontendEndPort
if ($null -eq $frontendPort) {
    Write-Host "No free frontend port found in range $FrontendStartPort-$FrontendEndPort." -ForegroundColor Red
    exit 1
}

Write-Host "Selected backend port: $backendPort" -ForegroundColor Green
Write-Host "Selected frontend port: $frontendPort" -ForegroundColor Green
Write-Host "Backend URL: http://localhost:$backendPort"
Write-Host "Frontend URL: http://localhost:$frontendPort"

if ($DryRun) {
    exit 0
}

$backendCommand = "set BACKEND_PORT=$backendPort&& cd /d `"$backendDir`" && mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=$backendPort"
$frontendCommand = "set BACKEND_PORT=$backendPort&& set FRONTEND_PORT=$frontendPort&& cd /d `"$frontendDir`" && npm run dev -- --port $frontendPort"

Start-Process cmd.exe -ArgumentList "/k", $backendCommand
Start-Process cmd.exe -ArgumentList "/k", $frontendCommand

Write-Host "Launcher started both processes." -ForegroundColor Cyan
