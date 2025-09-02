@echo off
REM Run the Whisper Transcriber on Windows

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if pip is installed
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Please ensure Python was installed with pip.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing required Python packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Check if GTK is installed
where gtk4-builder-tool >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo GTK4 is not installed. Please install GTK4 from https://www.gtk.org/docs/installations/windows/
    pause
    exit /b 1
)

:: Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: Run the application
echo Starting Whisper Transcriber...
python whisper_transcriber.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the application.
    echo Please make sure all dependencies are installed correctly.
    pause
    exit /b 1
)

exit /b 0
