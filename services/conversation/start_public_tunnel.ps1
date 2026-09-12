$ErrorActionPreference = 'Stop'
$config = Join-Path $env:USERPROFILE '.cloudflared\config-aero-public-chat.yml'
$cloudflared = 'C:\Program Files\cloudflared\cloudflared.exe'
if (-not (Test-Path -LiteralPath $cloudflared)) {
    $cloudflared = 'C:\Users\blyth\Desktop\Engineering\tools\cloudflared\cloudflared.exe'
}
if (-not (Test-Path -LiteralPath $cloudflared) -or -not (Test-Path -LiteralPath $config)) {
    throw 'Aero public tunnel binary or configuration is missing.'
}
$running = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'cloudflared.exe' -and $_.CommandLine -like '*config-aero-public-chat.yml*'
}
if ($running) {
    Write-Output 'Aero public tunnel is already running.'
    exit 0
}
$logs = Join-Path $env:USERPROFILE '.cloudflared\logs'
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$process = Start-Process -FilePath $cloudflared -ArgumentList @('tunnel', '--config', $config, 'run') `
    -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'aero-public-chat.out') `
    -RedirectStandardError (Join-Path $logs 'aero-public-chat.err') -PassThru
Start-Sleep -Seconds 3
if ($process.HasExited) { throw "Aero public tunnel exited immediately ($($process.ExitCode))." }
Write-Output "Aero public tunnel started (PID $($process.Id))."
