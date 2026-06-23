$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectDir

# Build app payload first
& "$ProjectDir\scripts\build-windows.ps1"

# Resolve Inno Setup compiler path
$PossibleIscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$Iscc = $PossibleIscc | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) {
    throw "Inno Setup compiler not found. Install Inno Setup 6 and rerun."
}

& $Iscc "$ProjectDir\packaging\windows\WeeWXDashboard.iss"

Write-Host "Installer build complete: $ProjectDir\dist\installer\"
