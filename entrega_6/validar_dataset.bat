@echo off
setlocal
cd /d "%~dp0"
title Validar dataset - LCML Entrega 6

if not exist "..\.venv\Scripts\python.exe" (
  echo  ERRO: ambiente .venv nao encontrado.
  pause
  exit /b 1
)

"..\.venv\Scripts\python.exe" "ferramentasalidar_dataset.py"

echo.
pause
