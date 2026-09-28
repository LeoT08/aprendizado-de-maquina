@echo off
setlocal
cd /d "%~dp0"
title Coleta Jokenpo - LCML Entrega 6

if not exist "..\.venv\Scripts\python.exe" (
  echo  ERRO: ambiente .venv nao encontrado em ..\.venv
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    Coleta de gestos - PEDRA, PAPEL, TESOURA
echo  ===============================================
echo.
echo  Meta: 45 imagens de cada gesto.
echo.
echo  NA JANELA:
echo    1 / 2 / 3   troca o gesto sem fechar
echo    A           liga a RAJADA (salva sozinho enquanto voce move a mao)
echo    ESPACO      salva um quadro
echo    Q           encerra
echo.
echo  Mantenha UMA mao dentro da caixa verde e varie angulo,
echo  distancia e posicao. Quadros quase identicos sao recusados.
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\coletar_gestos.py" %*

echo.
pause
