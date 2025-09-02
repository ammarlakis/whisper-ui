@echo off
echo Installing Whisper Transcriber for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Common solutions:
    echo 1. Install GTK4 using MSYS2: https://www.msys2.org/
    echo 2. Add MSYS2 to PATH: C:\msys64\mingw64\bin
    echo 3. Install Visual Studio Build Tools if needed
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo To run the application:
echo 1. Double-click run_transcriber.bat
echo 2. Or run: venv\Scripts\activate.bat && python whisper_transcriber.py
echo.
pause
