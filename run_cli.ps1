# VeritasRAG Terminal CLI Launcher for PowerShell
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[INFO] Found project virtual environment at .venv" -ForegroundColor Cyan
    & $venvPython (Join-Path $PSScriptRoot "veritas_cli.py")
} else {
    Write-Host "[WARNING] .venv not found. Trying system python..." -ForegroundColor Yellow
    python (Join-Path $PSScriptRoot "veritas_cli.py")
}
