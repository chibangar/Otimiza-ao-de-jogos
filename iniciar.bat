@echo off
title Midnight Optimizer
echo A iniciar Midnight Optimizer (sem consola)...
where pyw >nul 2>&1 && (start "" pyw app.py) || (where py >nul 2>&1 && (start "" py app.py) || (start "" pythonw app.py))
