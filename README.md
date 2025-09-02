# Whisper Transcriber

A GTK4 application for transcribing audio files using OpenAI's Whisper model.

## Features

- Select MP3 files for transcription
- Choose different Whisper models (tiny, base, small, medium, large)
- Select language or auto-detect
- Real-time progress tracking
- Cross-platform (Windows/Linux)

## Requirements

- Python 3.8+
- FFmpeg
- GTK4
- Python packages listed in `requirements.txt`

## Installation

1. Install system dependencies:

   **Windows:**
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH
   - Install GTK4 from [gtk.org](https://www.gtk.org/docs/installations/windows/)

   **Linux (Debian/Ubuntu):**
   ```bash
   sudo apt update
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 ffmpeg
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python whisper_transcriber.py
```

1. Click "Select Audio File" to choose an MP3 file
2. Select the desired model (larger models are more accurate but slower)
3. Choose the language or leave as "Auto-detect"
4. Click "Transcribe" to start the transcription
5. The progress bar will show the current status
6. The transcription will appear in the text area below

## Notes

- First run will download the selected Whisper model (can be several GB for larger models)
- Transcribing large files may take time, especially with larger models
- The application shows real-time progress and can be stopped at any time

## License

MIT
