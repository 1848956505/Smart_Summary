param(
    [int]$StartPort = 8080,
    [int]$EndPort = 8090,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Test-PortInUse {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return [bool]$conn
    } catch {
        return $false
    }
}

function Get-FreePort {
    param([int]$From, [int]$To)
    for ($p = $From; $p -le $To; $p++) {
        if (-not (Test-PortInUse -Port $p)) {
            return $p
        }
    }
    return $null
}

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

$freePort = Get-FreePort -From $StartPort -To $EndPort
if ($null -eq $freePort) {
    Write-Host "No free port found in range $StartPort-$EndPort." -ForegroundColor Red
    exit 1
}

$mvnArgs = @('spring-boot:run', "-Dspring-boot.run.arguments=--server.port=$freePort")

Write-Host "Selected backend port: $freePort" -ForegroundColor Green
Write-Host "Backend URL: http://localhost:$freePort"
Write-Host "Command: mvn $($mvnArgs -join ' ')"

if ($DryRun) {
    exit 0
}

& mvn @mvnArgs
exit $LASTEXITCODE
