@echo off
title Enviar Midnight Optimizer para o GitHub
color 0b
echo ==============================================================================
echo  🚀 A ENVIAR MIDNIGHT OPTIMIZER v3.1.0 PARA O GITHUB
echo  Repositorio: https://github.com/chibangar/Otimiza-ao-de-jogos
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/2] A enviar branch principal (main)...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O envio da branch principal falhou.
    echo Se abriu uma janela no navegador, faca login com a sua conta GitHub (chibangar).
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] A enviar tag de versao (v3.1.0) para ativar o GitHub Actions...
git push origin v3.1.0
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O envio da tag falhou.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo  SUCESSO! O seu codigo e a tag v3.1.0 estao agora no GitHub!
echo ==============================================================================
echo.
echo O GitHub Actions iniciou a compilacao automatica do MidnightOptimizer.exe!
echo Podes acompanhar a compilacao em:
echo https://github.com/chibangar/Otimiza-ao-de-jogos/actions
echo.
echo E ver o release publicado em:
echo https://github.com/chibangar/Otimiza-ao-de-jogos/releases
echo.
pause
