# Windows Installation Guide - Whisper Transcriber

This guide will help you install and run the Whisper Transcriber application on Windows.

## Prerequisites

### 1. Install Python 3.8+
- Download Python from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation
- Verify installation: Open Command Prompt and run `python --version`

### 2. Install GTK4 for Windows
GTK4 is required for the GUI interface.

**Option A: Using MSYS2 (Recommended)**
1. Download and install [MSYS2](https://www.msys2.org/)
2. Open MSYS2 terminal and run:
   ```bash
   pacman -S mingw-w64-x86_64-gtk4 mingw-w64-x86_64-python3-gobject
   ```
3. Add MSYS2 to your PATH: `C:\msys64\mingw64\bin`

**Option B: Using vcpkg**
1. Install [vcpkg](https://github.com/Microsoft/vcpkg)
2. Run: `vcpkg install gtk4`

### 3. Install Git (Optional)
- Download from [git-scm.com](https://git-scm.com/download/win)

## Installation Steps

### 1. Download the Project
**Option A: Using Git**
```cmd
git clone <repository-url>
cd windsurf-project
```

**Option B: Download ZIP**
- Download the project files
- Extract to a folder (e.g., `C:\whisper-transcriber`)

### 2. Create Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Install Additional Windows Dependencies
```cmd
pip install pywin32
```

## Running the Application

### Method 1: Using Batch File
Double-click `run_transcriber.bat` or run:
```cmd
run_transcriber.bat
```

### Method 2: Command Line
```cmd
venv\Scripts\activate
python whisper_transcriber.py
```

## Troubleshooting

### Common Issues

**1. "GTK not found" Error**
- Ensure GTK4 is properly installed
- Add GTK bin directory to PATH
- For MSYS2: Add `C:\msys64\mingw64\bin` to PATH

**2. "No module named 'gi'" Error**
```cmd
pip install PyGObject
```

**3. CUDA/GPU Issues**
- Install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) for GPU acceleration
- Or use CPU-only mode (automatically falls back)

**4. Audio File Issues**
- Install FFmpeg: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add FFmpeg to PATH

**5. Memory Issues**
- Use smaller Whisper models (tiny, base, small)
- Close other applications to free memory
- The app automatically falls back to CPU if GPU memory is insufficient

### Performance Tips

**For Better Performance:**
- Use GPU-enabled PyTorch if you have NVIDIA GPU
- Use SSD storage for faster file access
- Ensure sufficient RAM (4GB+ recommended)

**For Lower Resource Usage:**
- Use smaller models (tiny, base)
- Process shorter audio files
- Close unnecessary applications

## Supported Audio Formats
- MP3, WAV, M4A, FLAC, OGG
- Most common audio formats supported via FFmpeg

## Features
- Real-time transcription progress
- Multiple Whisper model sizes
- Language auto-detection
- Selectable and copyable text output
- Memory-efficient processing
- Automatic error recovery

## System Requirements
- **OS**: Windows 10/11
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 2GB free space
- **GPU**: Optional (NVIDIA GPU for acceleration)

## Getting Help
If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Try running with smaller audio files first
4. Check Windows Event Viewer for detailed error messages
