@echo off
setlocal
cd /d "%~dp0"
title Arena de Sumo - LCML Entrega 7

if not exist "..\.venv\Scripts\python.exe" (
  echo  ERRO: ambiente .venv nao encontrado em ..\.venv
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    Arena de sumo - Aula 7
echo  ===============================================
echo.
echo  A plataforma ENCOLHE depois de 15 segundos.
echo  Azul = robo A (seu)   Vermelho = robo B (bot ou rival)
echo.
echo  Deixe esta janela aberta e rode o notebook em outra.
echo  ESC ou fechar a janela encerra a arena.
echo.

"..\.venv\Scripts\python.exe" "ferramentas\arena_lcml.py" %*

echo.
pause
