# Windows Installer Creation Guide

This guide explains how to create a professional Windows installer for the Whisper Transcriber application.

## Overview

The installer system provides multiple options for packaging your application:

1. **PyInstaller** - Bundles Python application into standalone executable
2. **NSIS** - Creates professional Windows installer (recommended)
3. **Inno Setup** - Alternative installer creator with modern UI
4. **Automated Build Script** - Streamlines the entire process

## Prerequisites

### Required Software

1. **Python 3.8+** with pip
2. **Git** (optional, for version control)

### Installer Tools (choose one or both)

**NSIS (Recommended)**
- Download from: https://nsis.sourceforge.io/
- Add to PATH: `C:\Program Files (x86)\NSIS`
- Lightweight and widely used

**Inno Setup (Alternative)**
- Download from: https://jrsoftware.org/isinfo.php
- Add to PATH: `C:\Program Files (x86)\Inno Setup 6`
- Modern UI with advanced features

## Quick Start

### Automated Build (Recommended)

1. Open Command Prompt in project directory
2. Run the automated build script:
   ```cmd
   build_installer.bat
   ```
3. Follow the prompts to choose installer type
4. The script will handle everything automatically

### Manual Build Process

If you prefer manual control over the build process:

#### Step 1: Prepare Environment

```cmd
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install build dependencies
pip install -r requirements-build.txt
```

#### Step 2: Build Executable

```cmd
# Clean previous builds
rmdir /s /q dist build

# Build with PyInstaller
pyinstaller whisper_transcriber.spec --clean --noconfirm
```

#### Step 3: Create Installer

**For NSIS:**
```cmd
makensis installer.nsi
```

**For Inno Setup:**
```cmd
iscc installer.iss
```

## File Structure

After building, your project will have this structure:

```
whisper-transcriber/
├── dist/
│   └── WhisperTranscriber/          # Bundled application
│       ├── WhisperTranscriber.exe   # Main executable
│       └── [dependencies...]        # All required libraries
├── installer_output/                # Inno Setup output
│   └── WhisperTranscriber-1.0.0-Setup.exe
├── WhisperTranscriber-1.0.0-Setup.exe  # NSIS output
├── whisper_transcriber.spec         # PyInstaller configuration
├── installer.nsi                    # NSIS installer script
├── installer.iss                    # Inno Setup script
└── build_installer.bat              # Automated build script
```

## Installer Features

### NSIS Installer Features
- Professional Windows installer UI
- Automatic dependency detection
- File associations for audio files
- Start menu and desktop shortcuts
- Proper uninstaller
- Registry integration
- Upgrade detection

### Inno Setup Features
- Modern wizard-style interface
- Component selection
- Custom installation options
- File associations (optional)
- Windows version checking
- Running application detection
- Shell integration refresh

## Customization

### Changing Application Information

Edit the installer scripts to customize:

**In `installer.nsi` (NSIS):**
```nsis
!define APP_NAME "Your App Name"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company"
!define APP_URL "https://your-website.com"
```

**In `installer.iss` (Inno Setup):**
```ini
AppName=Your App Name
AppVersion=1.0.0
AppPublisher=Your Company
AppPublisherURL=https://your-website.com
```

### Adding Custom Files

**For NSIS:** Edit the `SecCore` section in `installer.nsi`
**For Inno Setup:** Edit the `[Files]` section in `installer.iss`

### Branding Assets

Create these optional files for professional appearance:
- `icon.ico` - Application icon (32x32, 48x48, 256x256)
- `LICENSE.txt` - License agreement
- `header.bmp` - Installer header image (150x57 pixels)
- `welcome.bmp` - Welcome page image (164x314 pixels)

## PyInstaller Configuration

The `whisper_transcriber.spec` file controls how PyInstaller bundles your application:

### Key Sections

- **`datas`** - Include additional files (configs, assets)
- **`binaries`** - Include external libraries and DLLs
- **`hiddenimports`** - Specify modules not automatically detected
- **`excludes`** - Remove unnecessary modules to reduce size

### GTK4 Considerations

The spec file automatically handles GTK4 dependencies by:
1. Detecting GTK installation paths
2. Including necessary typelibs and DLLs
3. Setting up proper library paths

## Troubleshooting

### Common Build Issues

**"PyInstaller not found"**
```cmd
pip install pyinstaller
```

**"GTK libraries not found"**
- Install GTK4 via MSYS2 or vcpkg
- Ensure GTK is in system PATH
- Update paths in `whisper_transcriber.spec`

**"Missing DLL errors"**
- Check `binaries` section in spec file
- Use Dependency Walker to identify missing DLLs
- Add missing libraries to `binaries` list

### Installer Issues

**"NSIS/Inno Setup not found"**
- Install the respective tool
- Add installation directory to system PATH
- Restart Command Prompt

**"File not found during installer creation"**
- Ensure PyInstaller build completed successfully
- Check that `dist/WhisperTranscriber/` exists
- Verify all referenced files exist

### Runtime Issues

**"Application won't start"**
- Set `console=True` in spec file for debugging
- Check Windows Event Viewer for error details
- Test on clean Windows system

**"Missing audio codecs"**
- Ensure FFmpeg is bundled or separately installed
- Include codec libraries in installer
- Test with various audio formats

## Distribution

### Testing Your Installer

1. Test on clean Windows 10/11 systems
2. Verify all features work correctly
3. Test installation and uninstallation
4. Check file associations
5. Validate shortcuts and registry entries

### Code Signing (Optional)

For professional distribution:

1. Obtain code signing certificate
2. Sign the executable:
   ```cmd
   signtool sign /f certificate.p12 /p password dist\WhisperTranscriber\WhisperTranscriber.exe
   ```
3. Sign the installer:
   ```cmd
   signtool sign /f certificate.p12 /p password WhisperTranscriber-1.0.0-Setup.exe
   ```

## Advanced Configuration

### Multiple Architecture Support

To support both 32-bit and 64-bit:

1. Create separate spec files for each architecture
2. Build on respective systems or use cross-compilation
3. Create architecture-specific installers
4. Use installer logic to detect system architecture

### Dependency Management

For complex dependencies:

1. Use `--collect-all` for problematic packages
2. Create custom hooks for special cases
3. Use `--add-data` for data files
4. Consider using conda-pack for conda environments

### Installer Localization

Both NSIS and Inno Setup support multiple languages:

**NSIS:**
```nsis
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
```

**Inno Setup:**
```ini
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
```

## Best Practices

1. **Version Management** - Use semantic versioning
2. **Testing** - Test on multiple Windows versions
3. **Documentation** - Include user manual and help files
4. **Updates** - Plan for automatic update mechanism
5. **Logging** - Include application logging for support
6. **Backup** - Keep installer sources in version control

## GitHub Actions CI/CD

### Automated Building with GitHub Actions

The project includes GitHub Actions workflows for automated Windows installer building:

#### Main Build Workflow (`.github/workflows/build-windows-installer.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch
- Release publication

**Features:**
- Builds on Windows runners with GTK4 support
- Creates both NSIS and Inno Setup installers
- Uploads artifacts for download
- Automatically attaches installers to releases

**Manual Trigger:**
```bash
# Go to GitHub Actions tab in your repository
# Click "Build Windows Installer" workflow
# Click "Run workflow" button
# Choose installer type: nsis, inno, or both
```

#### Test Workflow (`.github/workflows/test-build.yml`)

**Purpose:**
- Tests Python syntax and imports
- Validates code on multiple Python versions (3.8-3.11)
- Runs on Linux for faster feedback

### Setting Up CI/CD

1. **Push to GitHub:**
   ```bash
   git add .github/
   git commit -m "Add GitHub Actions workflows"
   git push origin main
   ```

2. **Enable Actions:**
   - Go to your repository on GitHub
   - Click "Actions" tab
   - Enable workflows if prompted

3. **First Build:**
   - Push any commit or create a pull request
   - Watch the build progress in Actions tab
   - Download artifacts when complete

### Downloading Built Installers

**From Workflow Runs:**
1. Go to Actions tab
2. Click on a completed workflow run
3. Scroll to "Artifacts" section
4. Download the installer files

**From Releases:**
- Installers are automatically attached to GitHub releases
- Users can download directly from the Releases page

### Customizing the Workflow

**Change Python Version:**
```yaml
strategy:
  matrix:
    python-version: ['3.11']  # Add more versions as needed
```

**Modify Build Triggers:**
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]  # Add more branches
    tags: [ 'v*' ]  # Trigger on version tags
```

**Add Code Signing:**
```yaml
- name: Sign executables
  run: |
    # Add your code signing steps here
    signtool sign /f ${{ secrets.CERT_FILE }} /p ${{ secrets.CERT_PASSWORD }} dist/WhisperTranscriber/WhisperTranscriber.exe
```

### Secrets Configuration

For advanced features, add these secrets in GitHub repository settings:

- `CERT_FILE` - Base64 encoded certificate file
- `CERT_PASSWORD` - Certificate password
- `SIGNING_KEY` - Code signing key

## Support and Resources

- **PyInstaller Documentation**: https://pyinstaller.org/
- **NSIS Documentation**: https://nsis.sourceforge.io/Docs/
- **Inno Setup Documentation**: https://jrsoftware.org/ishelp/
- **GTK4 Windows Guide**: https://www.gtk.org/docs/installations/windows/
- **GitHub Actions Documentation**: https://docs.github.com/en/actions

For project-specific issues, check the application logs and Windows Event Viewer for detailed error information.
