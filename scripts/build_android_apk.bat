@echo off
setlocal
cd /d "%~dp0\.."

python -m pip install --upgrade flet
flet build apk --product "Gerador de Senhas - RBS" --org "br.com.rbs" --project "gerador_senhas_rbs"

echo.
echo Concluido. Verifique a pasta build\apk.
pause
