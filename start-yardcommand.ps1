$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendRoot = Join-Path $projectRoot "yardcommand-ui"
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python virtual environment not found at $pythonExe"
    exit 1
}

if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    Write-Error "Frontend package.json not found at $frontendRoot"
    exit 1
}

$backendCommand = "Set-Location '$projectRoot'; & '$pythonExe' -m uvicorn backend.main:app --reload"
$frontendCommand = "Set-Location '$frontendRoot'; npm start"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Started YardCommand backend and frontend in separate PowerShell windows."
Write-Host "Backend: http://127.0.0.1:8000"
Write-Host "Frontend: http://localhost:3000/bills"
