param(
    [Parameter(Mandatory = $true)]
    [string]$InputCsv,
    [string]$AsOfDate = (Get-Date -Format 'yyyy-MM-dd')
)

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $workspace
& "$workspace/.venv/Scripts/python.exe" "$workspace/analyze_saas.py" $InputCsv --as-of-date $AsOfDate --output-dir $workspace
