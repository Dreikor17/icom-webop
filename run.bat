@echo off
REM Icom WebOp launcher for Windows
cd /d "%~dp0"
where py >nul 2>nul && (py run.py %*) || (python run.py %*)
pause
