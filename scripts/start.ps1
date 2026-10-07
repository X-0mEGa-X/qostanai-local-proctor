$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path '.venv/Scripts/python.exe')) { throw 'Run scripts/setup.ps1 first' }
if (!(Test-Path 'node_modules/electron/cli.js')) { throw 'Run npm ci first' }
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (!$nodeCommand) { throw 'Node.js is required' }
& $nodeCommand.Source node_modules/electron/cli.js .
