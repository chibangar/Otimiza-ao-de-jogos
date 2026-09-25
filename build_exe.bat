@echo off
title Midnight Optimizer - Build EXE
echo ============================================
echo  MIDNIGHT OPTIMIZER - A gerar .EXE nativo
echo ============================================
echo.

where py >nul 2>&1 && (set PYTHON_CMD=py) || (set PYTHON_CMD=python)

REM 1. Instalar dependencias
echo [1/3] A instalar dependencias...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt

REM 2. Gerar EXE com PyInstaller (janela sem consola, um ficheiro so)
echo.
echo [2/3] A compilar EXE...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean MidnightOptimizer.spec

echo.
echo [3/3] Pronto!
echo O teu EXE esta em: dist\MidnightOptimizer.exe
echo Clica com botao direito -^> Executar como administrador para poder total.
pause
