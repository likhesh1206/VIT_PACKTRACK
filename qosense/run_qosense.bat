@echo off
title QoSense — Intelligent QoS Monitoring & Traffic Prioritization System
cls
echo ======================================================================
echo    QoSense — Intelligent QoS Monitoring and Traffic Prioritization
echo ======================================================================
echo.

set UV_EXE=%USERPROFILE%\.local\bin\uv.exe

if exist "%UV_EXE%" (
    echo [*] Starting QoSense using uv runtime...
    "%UV_EXE%" run "%~dp0run.py"
) else if exist "%~dp0.venv\Scripts\uvicorn.exe" (
    echo [*] Starting QoSense using local venv...
    "%~dp0.venv\Scripts\uvicorn.exe" backend.main:app --host 127.0.0.1 --port 8000
) else (
    echo [*] Starting QoSense using default python...
    python "%~dp0run.py"
)

pause
