@echo off
REM Build Windows Installer for Whisper Transcriber
REM This script automates the entire build process

echo ========================================
echo Whisper Transcriber Installer Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade build dependencies
echo Installing build dependencies...
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist\" rmdir /s /q "dist\"
if exist "build\" rmdir /s /q "build\"
if exist "installer_output\" rmdir /s /q "installer_output\"

REM Create directories
mkdir "installer_output" 2>nul

REM Build executable with PyInstaller
echo Building executable with PyInstaller...
pyinstaller whisper_transcriber.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\WhisperTranscriber\WhisperTranscriber.exe" (
    echo ERROR: Executable not found after build
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable location: dist\WhisperTranscriber\WhisperTranscriber.exe
echo.

REM Ask user which installer to create
echo Choose installer type:
echo 1. NSIS Installer (recommended)
echo 2. Inno Setup Installer
echo 3. Both installers
echo 4. Skip installer creation
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto nsis_installer
if "%choice%"=="2" goto inno_installer
if "%choice%"=="3" goto both_installers
if "%choice%"=="4" goto end
goto invalid_choice

:nsis_installer
echo.
echo Creating NSIS installer...
REM Check if NSIS is installed
where makensis >nul 2>nul
if errorlevel 1 (
    echo ERROR: NSIS is not installed or not in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/
    echo Add NSIS installation directory to your PATH
    pause
    exit /b 1
)

makensis installer.nsi
if errorlevel 1 (
    echo ERROR: NSIS installer creation failed
    pause
    exit /b 1
)
echo NSIS installer created successfully!
goto end

:inno_installer
echo.
echo Creating Inno Setup installer...
REM Check if Inno Setup is installed
where iscc >nul 2>nul
if errorlevel 1 (
    echo ERROR: Inno Setup is not installed or not in PATH
    echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
    echo Add Inno Setup installation directory to your PATH
    pause
    exit /b 1
)

iscc installer.iss
if errorlevel 1 (
    echo ERROR: Inno Setup installer creation failed
    pause
    exit /b 1
)
echo Inno Setup installer created successfully!
goto end

:both_installers
echo.
echo Creating both installers...

REM NSIS
where makensis >nul 2>nul
if errorlevel 1 (
    echo WARNING: NSIS not found, skipping NSIS installer
) else (
    echo Creating NSIS installer...
    makensis installer.nsi
    if errorlevel 1 (
        echo WARNING: NSIS installer creation failed
    ) else (
        echo NSIS installer created successfully!
    )
)

REM Inno Setup
where iscc >nul 2>nul
if errorlevel 1 (
    echo WARNING: Inno Setup not found, skipping Inno Setup installer
) else (
    echo Creating Inno Setup installer...
    iscc installer.iss
    if errorlevel 1 (
        echo WARNING: Inno Setup installer creation failed
    ) else (
        echo Inno Setup installer created successfully!
    )
)
goto end

:invalid_choice
echo Invalid choice. Skipping installer creation.
goto end

:end
echo.
echo ========================================
echo Build process completed!
echo ========================================
echo.
echo Files created:
echo - Executable: dist\WhisperTranscriber\
if exist "WhisperTranscriber-1.0.0-Setup.exe" echo - NSIS Installer: WhisperTranscriber-1.0.0-Setup.exe
if exist "installer_output\WhisperTranscriber-1.0.0-Setup.exe" echo - Inno Setup Installer: installer_output\WhisperTranscriber-1.0.0-Setup.exe
echo.
echo You can now distribute the installer to end users.
echo.
pause
