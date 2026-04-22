param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$NoReload
)

Set-Location $PSScriptRoot

$reloadArgs = @()
if (-not $NoReload) {
    $reloadArgs += "--reload"
}

$pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

& $pythonExe -m uvicorn app.main:app --app-dir src --host $Host --port $Port @reloadArgs
