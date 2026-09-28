@echo off
setlocal
cd /d "%~dp0"
title Teste adverso ANTES - baseline

echo.
echo  ===============================================
echo    ETAPA 4 - teste de robustez  (1 de 2)
echo    Modelo BASELINE, luz fraca
echo  ===============================================
echo.
echo  A primeira tentativa nao valeu: a luz ficou so 11%
echo  mais escura (107 para 96) e varias rodadas foram
echo  registradas no mesmo segundo, contando o mesmo
echo  quadro varias vezes.
echo.
echo  Agora a ferramenta exige 2 segundos entre rodadas
echo  e mostra a LUZ no canto inferior direito.
echo.
echo  APAGUE A LUZ do ambiente de verdade. O numero da
echo  luz precisa ficar VERDE, ou seja abaixo de 60.
echo  Se ficar laranja, esta claro demais ainda.
echo.
echo  Faca 10 rodadas, variando os tres gestos, com a mao
echo  em posicoes diferentes a cada rodada.
echo      1 = PEDRA   2 = PAPEL   3 = TESOURA
echo      S = captura de tela    Q = encerra
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\jogar_rodadas.py" --modelo modelos/cnn_baseline.pt --rodadas 10 --condicao iluminacao_fraca --saida adverso_antes --luz-alvo 60

echo.
pause
