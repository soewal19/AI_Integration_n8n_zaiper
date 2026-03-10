param(
    [switch]$Quiet
)

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if ($Quiet) {
    python monitor.py --check --quiet
} else {
    python monitor.py --check
}

