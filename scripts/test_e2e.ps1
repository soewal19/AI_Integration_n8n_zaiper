Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..
python -m unittest tests\\test_e2e.py -v

