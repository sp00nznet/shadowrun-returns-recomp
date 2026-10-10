@echo off
rem Quick start: double-click. Checks prerequisites (and asks before installing
rem any), finds your copy of Shadowrun Returns, recompiles it and writes a
rem launcher. Rerun it after a failure: finished steps are skipped.
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Python 3 is needed to run the setup.
    choice /m "Install Python 3.12 with winget (about 30 MB)"
    if errorlevel 2 exit /b 1
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    echo Python is installed. Close this window and double-click Setup.cmd again.
    pause
    exit /b 0
)
py -3 tools\setup.py %*
pause
