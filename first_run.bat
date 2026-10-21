@echo off
TITLE STARK - First Run Setup
color 0a

echo ==================================================
echo      INSTALLING REQUIRED LIBRARIES...
echo ==================================================
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -m pip install -r requirements.txt
    py app.py
) else (
    pip install -r requirements.txt
    python app.py
)

pause