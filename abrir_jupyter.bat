@echo off
REM Abre o Jupyter Lab no notebook da Aula 1 com o ambiente do projeto
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERRO: ambiente .venv nao encontrado nesta pasta.
  echo Rode:  py -m venv .venv  ^&^&  .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
echo Abrindo o Jupyter Lab... o navegador abre sozinho.
echo Para encerrar, volte aqui e pressione Ctrl+C duas vezes.
echo.
".venv\Scripts\python.exe" -m jupyter lab aula01_camera.ipynb
pause
