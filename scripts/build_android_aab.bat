@echo off
setlocal
cd /d "%~dp0\.."

python -m pip install --upgrade flet
flet build aab --product "Gerador de Senhas - RBS" --org "br.com.rbs" --project "gerador_senhas_rbs"

echo.
echo Concluido. Verifique a pasta build\aab.
pause
