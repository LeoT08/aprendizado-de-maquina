@echo off
setlocal
cd /d "%~dp0"
title Teste adverso DEPOIS - com augmentation

if not exist "modelos\cnn_augmentation.pt" (
  echo  ERRO: modelo com augmentation nao encontrado.
  pause
  exit /b 1
)

echo.
echo  ===============================================
echo    ETAPA 5 - teste de robustez  (2 de 2)
echo    Modelo com AUGMENTATION, mesma luz fraca
echo  ===============================================
echo.
echo  Este e o MESMO teste de antes, trocando so o
echo  modelo. Para a comparacao valer:
echo.
echo    - mantenha a MESMA iluminacao (luz verde, abaixo de 60)
echo    - faca a MESMA sequencia de gestos
echo    - nao mude a distancia nem o fundo
echo.
echo  Se voce mudar qualquer outra coisa, a diferenca
echo  medida deixa de ser efeito do augmentation.
echo.
pause

"..\.venv\Scripts\python.exe" "ferramentas\jogar_rodadas.py" --modelo modelos/cnn_augmentation.pt --rodadas 10 --condicao iluminacao_fraca --saida adverso_depois --luz-alvo 60

echo.
pause
