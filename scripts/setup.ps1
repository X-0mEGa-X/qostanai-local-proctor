param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& $Python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or 3.12 is required' }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw 'CPU PyTorch installation failed' }
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed' }
& .\.venv\Scripts\python.exe scripts/download_models.py
if ($LASTEXITCODE -ne 0) { throw 'Model download failed' }
npm ci
if ($LASTEXITCODE -ne 0) { throw 'Node dependency installation failed' }
node node_modules/electron/install.js
if ($LASTEXITCODE -ne 0) { throw 'Electron runtime installation failed' }
Write-Output 'Setup complete. Run npm start.'
