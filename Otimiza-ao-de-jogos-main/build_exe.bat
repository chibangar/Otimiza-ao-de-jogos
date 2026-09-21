@echo off
title Midnight Optimizer - Build EXE
echo ============================================
echo  MIDNIGHT OPTIMIZER - A gerar .EXE nativo
echo ============================================
echo.

REM 1. Instalar dependencias
echo [1/3] A instalar dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 2. Gerar EXE com PyInstaller (janela sem consola, um ficheiro so)
echo.
echo [2/3] A compilar EXE...
python -m PyInstaller --noconfirm --onefile --windowed --icon "assets\icon.ico" --name "MidnightOptimizer" --add-data "index.html;." --add-data "styles.css;." --add-data "renderer.js;." --add-data "assets;assets" app.py

echo.
echo [3/3] Pronto!
echo O teu EXE esta em: dist\MidnightOptimizer.exe
echo Clica com botao direito -^> Executar como administrador para poder total.
pause
