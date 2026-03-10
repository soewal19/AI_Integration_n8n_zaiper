param(
    [int]$Interval = 60,
    [switch]$Quiet
)

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if ($Quiet) {
    python monitor.py --watch --interval $Interval --quiet
} else {
    python monitor.py --watch --interval $Interval
}

