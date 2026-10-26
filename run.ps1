# 包裝 run.py：優先使用專案內 venv 的 Python。
# 沒指定 -BindHost / -Port 時，沿用 run.py 的預設值（Port 來自 .env 的 APP_PORT）。
param(
    [string]$BindHost,
    [int]$Port,
    [switch]$NoReload
)

Set-Location $PSScriptRoot

$pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$runArgs = @()
if ($PSBoundParameters.ContainsKey("BindHost")) { $runArgs += @("--host", $BindHost) }
if ($PSBoundParameters.ContainsKey("Port")) { $runArgs += @("--port", $Port) }
if ($NoReload) { $runArgs += "--no-reload" }

& $pythonExe run.py @runArgs
