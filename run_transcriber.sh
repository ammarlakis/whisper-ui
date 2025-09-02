#!/bin/bash
# Run the Whisper Transcriber on Linux

# Exit on error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it with:"
    echo "sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install it with:"
    echo "sudo apt update && sudo apt install python3-pip"
    exit 1
fi

# Check if GTK4 is installed
if ! pkg-config --exists gtk4; then
    echo "GTK4 is not installed. Installing dependencies..."
    sudo apt update
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 ffmpeg
fi

# Install Python dependencies
echo "Installing required Python packages..."
pip3 install -r requirements.txt

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the application
echo "Starting Whisper Transcriber..."
python whisper_transcriber.py

exit 0
