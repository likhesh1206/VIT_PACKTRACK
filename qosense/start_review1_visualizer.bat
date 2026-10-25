@echo off
title CN Review 1 - Detection of Compromised Smart-Home Devices Visualizer
echo ==============================================================================
echo   Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour
echo   Computer Networks (CN) - Project Review 1 Visual Evaluation Suite
echo ==============================================================================
cd /d "%~dp0"

echo [*] Activating Python environment...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
) else (
    python run.py
)
pause
