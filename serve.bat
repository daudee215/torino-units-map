@echo off
cd /d "%~dp0"
echo Unita San Donato: http://localhost:8765
start "" http://localhost:8765
py -m http.server 8765 --bind 127.0.0.1
