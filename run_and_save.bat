@echo off
REM Run essentials and save output to output/runs/YYYYMMDD_HHmmss/
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
python scripts/run_and_save.py %*
echo.
pause
