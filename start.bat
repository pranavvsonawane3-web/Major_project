@echo off
title Devora AI - DevOps Intelligence Platform
echo ===================================================================
echo             DEVORA AI - DEVOPS INTELLIGENCE PLATFORM
echo ===================================================================
echo.
echo Starting local FastAPI backend server...
echo Serving web application at: http://127.0.0.1:8000
echo API Documentation at:       http://127.0.0.1:8000/docs
echo.
start http://127.0.0.1:8000
python server.py
pause
