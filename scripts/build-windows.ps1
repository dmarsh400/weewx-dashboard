$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectDir

python -m pip install --upgrade pyinstaller
pyinstaller --clean weewx_dashboard.spec

Write-Host "Windows build complete: $ProjectDir\dist\weewx-dashboard\"
