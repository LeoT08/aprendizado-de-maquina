@echo off
setlocal
cd /d "%~dp0"
title Rodar entrega da Aula 7 - LCML

if not exist "..\.venv\Scripts\python.exe" (
  echo  ERRO: ambiente .venv nao encontrado em ..\.venv
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    Entrega da Aula 7 de ponta a ponta
echo  ===============================================
echo.
echo  1. treina o lutador rival da Copa
echo  2. sobe a arena sem janela
echo  3. executa o notebook inteiro pelo protocolo TCP
echo  4. exporta o HTML e enche a pasta entregas\
echo.
echo  Leva alguns minutos: sao 13 lutas em tempo real.
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\executar_entrega.py" %*

echo.
pause
