@echo off
cd /d "%~dp0"
if not exist output\ingestion mkdir output\ingestion
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue)) { Start-Process py -ArgumentList '-u','-m','http.server','8765','--bind','127.0.0.1' -WindowStyle Hidden -WorkingDirectory (Get-Location).Path -RedirectStandardOutput 'output/ingestion/static-service.log' -RedirectStandardError 'output/ingestion/static-service-error.log' }; if (-not (Get-NetTCPConnection -LocalPort 8766 -State Listen -ErrorAction SilentlyContinue)) { Start-Process py -ArgumentList '-u','scripts/serve_registry.py' -WindowStyle Hidden -WorkingDirectory (Get-Location).Path -RedirectStandardOutput 'output/ingestion/review-service.log' -RedirectStandardError 'output/ingestion/review-service-error.log' }"
start "" http://127.0.0.1:8765/#lotto-1175-434
