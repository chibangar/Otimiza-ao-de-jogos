@echo off
title Pulse Gaming Optimizer
echo A iniciar Pulse Gaming Optimizer (sem consola)...
where pyw >nul 2>&1 && (start "" pyw app.py) || (where py >nul 2>&1 && (start "" py app.py) || (start "" pythonw app.py))
