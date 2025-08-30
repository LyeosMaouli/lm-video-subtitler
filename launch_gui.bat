@echo off
echo Video Subtitle Processor GUI
echo ============================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo Environment file not found. Creating from template...
    copy env.example .env
    echo.
    echo Please edit .env file with your LARA access credentials
    echo Then run this script again
    pause
    exit /b 1
)

echo.
echo Launching GUI application...
echo.

REM Run the GUI application
python gui.py

pause
