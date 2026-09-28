@echo off
setlocal
cd /d "%~dp0"
title Jokenpo - 10 rodadas (condicao normal)

if not exist "modelos\cnn_baseline.pt" (
  echo  ERRO: modelo nao encontrado. Treine a CNN no notebook primeiro.
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    ETAPA 3 - 10 rodadas de Jokenpo (normal)
echo  ===============================================
echo.
echo  A previsao da CNN aparece ao vivo, com as barras
echo  de probabilidade das tres classes.
echo.
echo  Faca o gesto e pressione a tecla do gesto que VOCE
echo  esta fazendo - e isso que define o "gesto real":
echo.
echo      1 = PEDRA     2 = PAPEL     3 = TESOURA
echo      S = salva uma captura de tela
echo      Q = encerra e grava o CSV
echo.
echo  Faca as 10 rodadas em condicao NORMAL (luz boa,
echo  mao centralizada). Erre de proposito nao - jogue
echo  como se fosse usar de verdade.
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\jogar_rodadas.py" --rodadas 10 --condicao normal --saida 10_rodadas_normal

echo.
pause
