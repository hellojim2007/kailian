$ErrorActionPreference = 'Stop'
$taskProject = $PSScriptRoot
$taskPython = (Get-Command python -ErrorAction Stop).Source
try {
    $taskHealth = Invoke-RestMethod 'http://127.0.0.1:8766/api/health' -TimeoutSec 2
} catch {
    Start-Process -FilePath $taskPython -ArgumentList @('"' + (Join-Path $taskProject 'server.py') + '"') -WorkingDirectory $taskProject -WindowStyle Hidden
    Start-Sleep -Seconds 2
}
Start-Process 'http://127.0.0.1:8766'
