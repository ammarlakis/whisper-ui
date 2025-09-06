from PyInstaller.utils.hooks import collect_data_files

# Collect Whisper package assets (e.g., mel_filters.npz) so runtime can find them
datas = collect_data_files('whisper', includes=['assets/*'])

