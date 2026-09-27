# VeritasRAG Terminal CLI Launcher from UI folder
$root = Join-Path $PSScriptRoot ".."
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$cliScript = Join-Path $root "veritas_cli.py"

if (Test-Path $venvPython) {
    Write-Host "[INFO] Found project virtual environment at ..\.venv" -ForegroundColor Cyan
    & $venvPython $cliScript
} else {
    Write-Host "[WARNING] ..\.venv not found. Trying system python..." -ForegroundColor Yellow
    python $cliScript
}
