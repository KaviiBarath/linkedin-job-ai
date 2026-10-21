@echo off
TITLE STARK LinkedIn Auto Applicant - Live Dashboard & Engine
color 0a

echo ==================================================
echo      STARTING STARK LINKEDIN AUTOMATION SERVER...
echo ==================================================
echo.
echo [*] Launching web dashboard on http://127.0.0.1:5001...
echo [*] Chrome browser will launch automatically upon starting automation.
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py app.py
) else (
    python app.py
)

pause