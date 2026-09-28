@echo off
setlocal
cd /d "%~dp0"
title Regravar as demonstracoes na mao - LCML Entrega 7

if not exist "..\.venv\Scripts\python.exe" (
  echo  ERRO: ambiente .venv nao encontrado em ..\.venv
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    Etapa 2 na mao: voce e o lutador
echo  ===============================================
echo.
echo  Este atalho coloca a etapa 2 em modo manual, abre a arena
echo  numa janela e abre o notebook. Dai em diante:
echo.
echo    1. rode a celula 1 (conectar)
echo    2. rode a celula 2 - abre a janelinha de controle
echo    3. clique NELA e lute com as SETAS
echo       cima = frente   baixo = freio   esquerda/direita = girar
echo    4. empurre o vermelho para fora sem cair junto
echo    5. feche a janelinha quando tiver umas 3 lutas
echo    6. rode as celulas 3 em diante para retreinar
echo.
echo  Para voltar ao piloto por regras depois:
echo    ferramentas\alternar_piloto.py --automatico
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\alternar_piloto.py" --manual
if errorlevel 1 (
  echo  ERRO ao alternar o modo do notebook.
  pause
  exit /b 1
)

start "Arena de Sumo - Aula 7" "..\.venv\Scripts\python.exe" "ferramentas\arena_lcml.py"

echo.
echo  Arena aberta em outra janela. Abrindo o Jupyter...
echo  Para encerrar tudo: feche a arena e pressione Ctrl+C duas vezes aqui.
echo.

"..\.venv\Scripts\python.exe" -m jupyter lab aula07_sumo_ia.ipynb

echo.
pause
