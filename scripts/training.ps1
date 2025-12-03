<#
.SYNOPSIS
    Training CLI wrapper for CodeAgents.

.DESCRIPTION
    Wrapper script to execute CodeAgents training commands.

.EXAMPLE
    .\training.ps1 skeleton Composer
#>

param(
    [Parameter(Mandatory=$false, Position=0)]
    [string]$Command,

    [Parameter(Mandatory=$false, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "CodeAgents\core\cli.py"

# Check if python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Construct the command
$CmdArgs = @($PythonScript)
if ($Command) {
    $CmdArgs += $Command
}
if ($Arguments) {
    $CmdArgs += $Arguments
}

# Execute python script
& python $CmdArgs
