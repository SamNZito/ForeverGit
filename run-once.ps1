# Fallback only. Prefer GitHub Actions so the PC can be off.
Set-Location $PSScriptRoot
python green.py once --push
