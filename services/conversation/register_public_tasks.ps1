$ErrorActionPreference = 'Stop'
$ps = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$pythonw = Join-Path (Split-Path (Get-Command python.exe).Source) 'pythonw.exe'
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user
$tunnel = Join-Path $PSScriptRoot 'start_public_tunnel.ps1'
$tunnelAction = New-ScheduledTaskAction -Execute $ps `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$tunnel`""
Register-ScheduledTask -TaskName 'Aero Public Chat Tunnel' -Action $tunnelAction `
    -Trigger @($logon, $repeat) -Principal $principal -Settings $settings -Force | Out-Null
$monitor = Join-Path $PSScriptRoot 'monitor_public.py'
$monitorAction = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$monitor`""
Register-ScheduledTask -TaskName 'Aero Public Chat Health' -Action $monitorAction `
    -Trigger $repeat -Principal $principal -Settings $settings -Force | Out-Null
Write-Output 'Registered Aero public tunnel and external health tasks.'
