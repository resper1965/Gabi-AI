@echo off
echo Copiando logo do Windows para WSL...
copy "C:\Users\resper\Downloads\gabi.svg" "\\wsl$\Ubuntu\home\resper\gabi-ai\nova-aplicacao\frontend\public\logo.svg"
if %errorlevel% equ 0 (
    echo Logo copiado com sucesso!
    echo Arquivo salvo em: \\wsl$\Ubuntu\home\resper\gabi-ai\nova-aplicacao\frontend\public\logo.svg
) else (
    echo Erro ao copiar o arquivo.
    echo Verifique se o arquivo existe em C:\Users\resper\Downloads\gabi.svg
)
pause 