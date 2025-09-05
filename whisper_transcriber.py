import os
import threading
import subprocess
import sys
import gc
import weakref
import signal
import atexit

from pathlib import Path
from datetime import timedelta

# Bootstrap GTK/GI environment for frozen (PyInstaller) builds on Windows
def _bootstrap_gtk_env():
    try:
        base_dir = None
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Ensure DLL search path includes our bundle
        if hasattr(os, 'add_dll_directory') and os.name == 'nt':
            try:
                os.add_dll_directory(base_dir)
                bin_dir = os.path.join(base_dir, 'bin')
                if os.path.isdir(bin_dir):
                    os.add_dll_directory(bin_dir)
            except Exception:
                pass

        # GI typelibs
        candidates = [
            os.path.join(base_dir, 'gi_typelibs'),
            os.path.join(base_dir, 'lib', 'girepository-1.0'),
            os.path.join(base_dir, 'girepository-1.0'),
        ]
        for p in candidates:
            if os.path.isdir(p):
                os.environ['GI_TYPELIB_PATH'] = p + os.pathsep + os.environ.get('GI_TYPELIB_PATH', '')
                break

        # GTK data (themes, schemas)
        share_dir = os.path.join(base_dir, 'share')
        if os.path.isdir(share_dir):
            os.environ['XDG_DATA_DIRS'] = share_dir + os.pathsep + os.environ.get('XDG_DATA_DIRS', '')

        # GDK pixbuf loaders
        gdk_loaders_dir = os.path.join(base_dir, 'lib', 'gdk-pixbuf-2.0', '2.10.0', 'loaders')
        if os.path.isdir(gdk_loaders_dir):
            os.environ['GDK_PIXBUF_MODULEDIR'] = gdk_loaders_dir
            cache = os.path.join(base_dir, 'lib', 'gdk-pixbuf-2.0', '2.10.0', 'loaders.cache')
            if os.path.exists(cache):
                os.environ['GDK_PIXBUF_MODULE_FILE'] = cache
    except Exception:
        pass

_bootstrap_gtk_env()

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Gio, GLib, Adw
except Exception as e:
    # Provide a visible error on Windows if GTK cannot be initialized
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, f"Failed to initialize GTK:\n{e}", "Whisper Transcriber", 0x10)
        except Exception:
            pass
    raise

class WhisperTranscriber(Adw.Application):    
    def __init__(self):
        super().__init__(application_id='com.example.whispertranscriber')
        self.connect('activate', self.on_activate)
        self.window = None
        self.transcription_thread = None
        self.transcription_process = None
        self.stop_transcription = threading.Event()
        self.current_progress = 0.0
        self.total_duration = 0
        self.whisper_model = None
        self._cleanup_registered = False
        
        # Register cleanup handlers
        self._register_cleanup_handlers()
        
    def on_activate(self, app):
        self.window = MainWindow(application=app)
        self.window.present()
    
    def _register_cleanup_handlers(self):
        """Register cleanup handlers for graceful shutdown"""
        if not self._cleanup_registered:
            atexit.register(self._cleanup_resources)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            self._cleanup_registered = True
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"Received signal {signum}, cleaning up...")
        self._cleanup_resources()
        sys.exit(0)
    
    def _cleanup_resources(self):
        """Clean up resources on application exit"""
        try:
            if self.window:
                self.window.cleanup_resources()
            
            # Clean up Whisper model
            if hasattr(self, 'whisper_model') and self.whisper_model is not None:
                del self.whisper_model
                self.whisper_model = None
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Whisper Transcriber")
        self.set_default_size(800, 600)
        self.set_resizable(True)
        
        # Connect close request signal to handle cleanup
        self.connect("close-request", self.on_close_request)
        
        # Initialize resource management
        self.whisper_model = None
        self.transcription_thread = None
        self.stop_transcription = threading.Event()
        self._model_cache = {}
        
        # Create main container with headerbar
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Create headerbar with native close button
        self.headerbar = Adw.HeaderBar()
        self.headerbar.set_title_widget(Adw.WindowTitle(title="Whisper Transcriber"))
        main_box.append(self.headerbar)
        
        # Main content layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.box.set_margin_top(12)
        self.box.set_margin_bottom(12)
        self.box.set_margin_start(12)
        self.box.set_margin_end(12)
        main_box.append(self.box)
        
        self.set_content(main_box)
        
        # File selection
        self.file_chooser_button = Gtk.Button(label="Select Audio File")
        self.file_chooser_button.connect("clicked", self.on_file_clicked)
        self.box.append(self.file_chooser_button)
        
        # Selected file label
        self.file_label = Gtk.Label(label="No file selected")
        self.file_label.set_halign(Gtk.Align.START)
        self.box.append(self.file_label)
        
        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        model_label = Gtk.Label(label="Model:")
        self.model_combo = Gtk.DropDown.new_from_strings(["tiny", "base", "small", "medium", "large"])
        self.model_combo.set_selected(2)  # Default to 'small'
        model_box.append(model_label)
        model_box.append(self.model_combo)
        self.box.append(model_box)
        
        # Language selection
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lang_label = Gtk.Label(label="Language:")
        self.lang_combo = Gtk.DropDown.new_from_strings(["Auto-detect", "Arabic", "English", "Spanish", "French", "German"])
        lang_box.append(lang_label)
        lang_box.append(self.lang_combo)
        self.box.append(lang_box)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.box.append(self.progress_bar)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.box.append(self.status_label)
        
        # Transcription output - using TextView for selectable text
        self.output_textview = Gtk.TextView()
        self.output_textview.set_editable(False)
        self.output_textview.set_cursor_visible(False)
        self.output_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_textview.set_hexpand(True)
        self.output_textview.set_vexpand(True)
        
        # Get the text buffer
        self.output_buffer = self.output_textview.get_buffer()
        self.output_buffer.set_text("Transcription will appear here")
        
        # Scrolled window for output
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.output_textview)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.box.append(scrolled)
        
        # Buttons
        button_box = Gtk.Box(spacing=6)
        self.transcribe_button = Gtk.Button(label="Transcribe")
        self.transcribe_button.connect("clicked", self.on_transcribe_clicked)
        self.transcribe_button.set_sensitive(False)
        
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        self.stop_button.set_sensitive(False)
        
        button_box.append(self.transcribe_button)
        button_box.append(self.stop_button)
        self.box.append(button_box)
        
        self.selected_file = None
        self.stop_transcription = threading.Event()
        
    def on_file_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Audio File")
        
        # Create file filter for audio files
        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audio files")
        filter_audio.add_mime_type("audio/*")
        filter_audio.add_pattern("*.mp3")
        filter_audio.add_pattern("*.wav")
        filter_audio.add_pattern("*.m4a")
        filter_audio.add_pattern("*.flac")
        filter_audio.add_pattern("*.ogg")
        
        # Create filter list and add our filter
        filter_list = Gio.ListStore.new(Gtk.FileFilter)
        filter_list.append(filter_audio)
        dialog.set_filters(filter_list)
        
        dialog.open(self, None, self.on_file_dialog_response, None)
        
    def on_file_dialog_response(self, dialog, result, user_data):
        try:
            file = dialog.open_finish(result)
            if file:
                self.selected_file = file.get_path()
                self.file_label.set_text(f"Selected: {os.path.basename(self.selected_file)}")
                self.transcribe_button.set_sensitive(True)
                self.update_status("Ready to transcribe")
        except Exception as e:
            print(f"File selection cancelled or failed: {e}")
            pass
        
    def on_transcribe_clicked(self, button):
        if not self.selected_file:
            self.update_status("No file selected")
            return
            
        self.transcribe_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.output_buffer.set_text("Transcribing...")
        self.progress_bar.set_fraction(0.0)
        
        # Get selected parameters
        model = self.model_combo.get_selected_item().get_string()
        lang = self.lang_combo.get_selected_item().get_string()
        if lang == "Auto-detect":
            lang = None
            
        # Start transcription in a separate thread
        self.transcription_thread = threading.Thread(
            target=self.run_transcription,
            args=(self.selected_file, model, lang)
        )
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        
    def on_stop_clicked(self, button):
        self.stop_button.set_sensitive(False)
        self.update_status("Stopping...")
        self.stop_transcription.set()
        
    def cleanup_resources(self):
        """Clean up all resources used by the window"""
        try:
            # Stop any running transcription
            if hasattr(self, 'stop_transcription'):
                self.stop_transcription.set()
            
            # Wait for transcription thread to finish
            if hasattr(self, 'transcription_thread') and self.transcription_thread and self.transcription_thread.is_alive():
                self.transcription_thread.join(timeout=3.0)
            
            # Clean up Whisper model
            if hasattr(self, 'whisper_model') and self.whisper_model is not None:
                del self.whisper_model
                self.whisper_model = None
            
            # Clear model cache
            if hasattr(self, '_model_cache'):
                self._model_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"Error during resource cleanup: {e}")
    
    def on_close_request(self, window):
        """Handle window close request with proper cleanup"""
        self.cleanup_resources()
        return False  # Allow window to close
    
    def _load_model_safely(self, model_name):
        """Load Whisper model with memory management and caching"""
        try:
            import whisper
            import torch
            
            # Check if model is already cached
            if model_name in self._model_cache:
                cached_model = self._model_cache[model_name]
                if cached_model is not None:
                    return cached_model
            
            # Clear any existing model to free memory
            if self.whisper_model is not None:
                del self.whisper_model
                self.whisper_model = None
                gc.collect()
            
            # Set memory-efficient options for PyTorch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Load model with error handling
            try:
                model = whisper.load_model(model_name)
                
                # Cache the model
                self._model_cache[model_name] = model
                self.whisper_model = model
                
                return model
                
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    # Try to recover from OOM by clearing cache and retrying
                    self._model_cache.clear()
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    
                    # Retry with smaller model if possible
                    if model_name in ['large', 'medium']:
                        fallback_model = 'base' if model_name == 'large' else 'tiny'
                        GLib.idle_add(self.update_status, f"Memory issue, falling back to {fallback_model} model...")
                        return whisper.load_model(fallback_model)
                    else:
                        raise e
                else:
                    raise e
                    
        except Exception as e:
            error_msg = f"Failed to load model {model_name}: {str(e)}"
            print(error_msg)
            GLib.idle_add(self.update_status, error_msg)
            raise e
        
    def run_transcription(self, file_path, model_name, language):
        try:
            import whisper
            import torch
            import warnings
            import threading
            import time
            import sys
            import io
            from contextlib import redirect_stderr
            
            # Suppress FP16 warning on CPU
            warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
            
            # Reset stop event
            self.stop_transcription.clear()
            accumulated_text = ""
            processed_segments = 0
            
            # Update status
            GLib.idle_add(self.update_status, f"Loading {model_name} model...")
            GLib.idle_add(self.update_progress, 0, "Loading model...")
            
            # Load the model with memory management
            model = self._load_model_safely(model_name)
            
            if self.stop_transcription.is_set():
                GLib.idle_add(self.on_transcription_finished, "Transcription stopped by user")
                return
            
            GLib.idle_add(self.update_progress, 0, "Model loaded, starting transcription...")
            
            # Set up parameters
            lang_param = language.lower() if language and language != "Auto-detect" else None
            kwargs = {
                'task': 'transcribe',
                'language': lang_param
            }
            
            # Custom progress tracking with stderr capture
            class ProgressCapture:
                def __init__(self, parent):
                    self.parent = parent
                    self.buffer = io.StringIO()
                    
                def write(self, text):
                    self.buffer.write(text)
                    # Look for progress patterns like "14%|█████▉| 32474/239186"
                    import re
                    progress_match = re.search(r'(\d+)%\|.*?\|\s*(\d+)/(\d+)', text)
                    if progress_match:
                        percent = int(progress_match.group(1))
                        current = int(progress_match.group(2))
                        total = int(progress_match.group(3))
                        
                        progress_fraction = 0.3 + (percent / 100.0) * 0.6  # Scale to 30-90%
                        status_msg = f"Processing: {percent}% ({current:,}/{total:,} frames)"
                        GLib.idle_add(self.parent.update_progress, progress_fraction, status_msg)
                    
                    # Look for language detection
                    if "Detected language:" in text:
                        lang_match = re.search(r'Detected language: (\w+)', text)
                        if lang_match:
                            detected_lang = lang_match.group(1)
                            GLib.idle_add(self.parent.update_status, f"Detected language: {detected_lang}")
                    
                    return len(text)
                    
                def flush(self):
                    pass
            
            # Create progress capture
            progress_capture = ProgressCapture(self)
            
            GLib.idle_add(self.update_progress, 0.0, "Processing audio...")
            
            # Custom transcribe function that processes segments in real-time
            def transcribe_with_segments():
                try:
                    import whisper.audio
                    import whisper.decoding
                    import numpy as np
                    
                    # Load and prepare audio (don't trim the full audio yet)
                    audio = whisper.load_audio(file_path)
                    original_duration = len(audio) / 16000  # Duration in seconds
                    
                    # Detect language using first 30 seconds
                    sample_for_detection = whisper.pad_or_trim(audio)
                    mel_sample = whisper.log_mel_spectrogram(sample_for_detection).to(model.device)
                    
                    # Detect the spoken language if not specified
                    if kwargs.get('language') is None:
                        _, probs = model.detect_language(mel_sample)
                        detected_language = max(probs, key=probs.get)
                        kwargs['language'] = detected_language
                        GLib.idle_add(self.update_status, f"Detected language: {detected_language} (Duration: {original_duration:.1f}s)")
                    
                    # Set up decoding options
                    decode_options = whisper.DecodingOptions(
                        language=kwargs.get('language'),
                        task=kwargs.get('task', 'transcribe'),
                        fp16=False  # Use FP32 for better compatibility
                    )
                    
                    # Process audio in chunks for real-time results
                    segments = []
                    chunk_duration = 30  # 30-second chunks
                    sample_rate = 16000
                    chunk_samples = chunk_duration * sample_rate
                    
                    accumulated_text = ""
                    total_chunks = (len(audio) + chunk_samples - 1) // chunk_samples
                    
                    GLib.idle_add(self.update_status, f"Processing {total_chunks} chunks...")
                    
                    for i in range(0, len(audio), chunk_samples):
                        if self.stop_transcription.is_set():
                            break
                            
                        # Extract chunk
                        chunk = audio[i:i + chunk_samples]
                        chunk_num = (i // chunk_samples) + 1
                        
                        # Skip very short chunks (less than 1 second)
                        if len(chunk) < sample_rate:
                            continue
                        
                        # Pad chunk to Whisper's expected length (30 seconds)
                        chunk_padded = whisper.pad_or_trim(chunk)
                        chunk_mel = whisper.log_mel_spectrogram(chunk_padded).to(model.device)
                        
                        # Decode chunk
                        try:
                            result = whisper.decode(model, chunk_mel, decode_options)
                            
                            if result.text.strip():
                                # Calculate timing for this chunk
                                start_time = i / sample_rate
                                end_time = min((i + len(chunk)) / sample_rate, len(audio) / sample_rate)
                                
                                # Create segment
                                segment = {
                                    'start': start_time,
                                    'end': end_time,
                                    'text': result.text.strip()
                                }
                                segments.append(segment)
                                
                                # Send partial result immediately
                                chunk_text = f"[{str(timedelta(seconds=int(start_time)))} --> {str(timedelta(seconds=int(end_time)))}]  {result.text.strip()}\n\n"
                                accumulated_text += chunk_text
                                
                                # Update UI with partial result
                                GLib.idle_add(self.update_transcription_text, accumulated_text.strip())
                                
                                # Update progress
                                progress = (i / len(audio)) * 1.0
                                chunk_num = (i // chunk_samples) + 1
                                total_chunks = (len(audio) + chunk_samples - 1) // chunk_samples
                                GLib.idle_add(self.update_progress, progress, f"Processing chunk {chunk_num}/{total_chunks}...")
                        
                        except Exception as chunk_error:
                            print(f"Error processing chunk {i//chunk_samples + 1}: {chunk_error}")
                            continue
                    
                    # Return final result
                    return {
                        'text': accumulated_text.strip(),
                        'segments': segments,
                        'language': kwargs.get('language')
                    }
                    
                except Exception as e:
                    raise e
            
            # Thread-safe transcription wrapper with cancellation support
            transcription_result = [None]
            transcription_error = [None]
            transcription_complete = threading.Event()
            
            def run_transcription_thread():
                try:
                    result = transcribe_with_segments()
                    transcription_result[0] = result
                except Exception as e:
                    # Handle memory errors in the transcription thread
                    if "CUDA out of memory" in str(e) or "out of memory" in str(e).lower():
                        try:
                            # Clear memory and try with CPU
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()
                            gc.collect()
                            
                            # Force CPU usage for memory-constrained systems
                            import whisper
                            model_cpu = whisper.load_model(model_name, device="cpu")
                            GLib.idle_add(self.update_status, "Memory issue detected, using CPU...")
                            
                            # Retry transcription with CPU
                            result = model_cpu.transcribe(file_path, verbose=True, **kwargs)
                            transcription_result[0] = result
                        except Exception as cpu_error:
                            transcription_error[0] = cpu_error
                    else:
                        transcription_error[0] = e
                finally:
                    transcription_complete.set()
            
            # Run transcription with real-time segment processing
            def process_transcription():
                nonlocal accumulated_text, processed_segments
                
                try:
                    GLib.idle_add(self.update_progress, 0.0, "Transcribing segments...")
                    
                    # Set up timeout and memory monitoring
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # Start transcription in a separate thread for cancellation support
                    transcription_start = time.time()
                    
                    # Start the transcription thread
                    transcription_thread = threading.Thread(target=run_transcription_thread)
                    transcription_thread.daemon = True
                    transcription_thread.start()
                    
                    # Wait for completion or cancellation with periodic checks
                    while not transcription_complete.is_set():
                        if self.stop_transcription.is_set():
                            GLib.idle_add(self.on_transcription_finished, "Transcription stopped by user")
                            return
                        
                        # Check every 100ms for responsiveness
                        transcription_complete.wait(timeout=0.1)
                    
                    # Check if there was an error
                    if transcription_error[0] is not None:
                        raise transcription_error[0]
                    
                    result = transcription_result[0]
                    
                    # Validate result
                    if result is None:
                        raise Exception("Transcription returned no result")
                    
                    transcription_time = time.time() - transcription_start
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # Report transcription completion information in the UI
                    memory_change = current_memory - initial_memory
                    memory_info = f"Memory: {initial_memory:.1f}MB → {current_memory:.1f}MB ({memory_change:+.1f}MB)"
                    completion_info = f"Completed in {transcription_time:.1f}s • {memory_info}"
                    GLib.idle_add(self.update_status, completion_info)
                    
                    if self.stop_transcription.is_set():
                        return
                    
                    # Final completion - segments were already processed in real-time
                    if self.stop_transcription.is_set():
                        return
                    
                    GLib.idle_add(self.update_progress, 1.0, "Transcription complete")
                    
                    # Final result - use the text from our custom transcription
                    final_text = result.get('text', 'No transcription available')
                    GLib.idle_add(self.on_transcription_complete, final_text)
                        
                except Exception as e:
                    if self.stop_transcription.is_set():
                        GLib.idle_add(self.on_transcription_finished, "Transcription stopped by user")
                    else:
                        raise e
            
            # Start transcription in a separate thread
            transcription_thread = threading.Thread(target=process_transcription)
            transcription_thread.daemon = True
            transcription_thread.start()
            
            # Wait for completion or cancellation
            while transcription_thread.is_alive():
                if self.stop_transcription.is_set():
                    GLib.idle_add(self.on_transcription_finished, "Transcription stopped by user")
                    return
                time.sleep(0.1)
            
        except Exception as e:
            import traceback
            
            # Enhanced error handling to prevent crashes
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Log detailed error for debugging
            full_traceback = traceback.format_exc()
            print(f"Transcription error ({error_type}): {error_msg}")
            print(f"Full traceback:\n{full_traceback}")
            
            # Clean up resources on error
            try:
                if hasattr(self, 'whisper_model') and self.whisper_model is not None:
                    del self.whisper_model
                    self.whisper_model = None
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass  # Ignore cleanup errors
            
            # Provide user-friendly error messages
            user_msg = "Error during transcription"
            if "out of memory" in error_msg.lower():
                user_msg = "Out of memory. Try a smaller model or shorter audio file."
            elif "file not found" in error_msg.lower() or "no such file" in error_msg.lower():
                user_msg = "Audio file not found or inaccessible."
            elif "unsupported format" in error_msg.lower():
                user_msg = "Unsupported audio format. Try MP3, WAV, or M4A."
            elif "cuda" in error_msg.lower():
                user_msg = "GPU error. Falling back to CPU processing."
            
            GLib.idle_add(self.on_transcription_finished, user_msg)
    
    def update_transcription_text(self, text):
        """Update the transcription text in real-time"""
        self.output_buffer.set_text(text)
        
        # Auto-scroll to bottom to show latest text
        mark = self.output_buffer.get_insert()
        self.output_textview.scroll_mark_onscreen(mark)
    
    def update_progress(self, fraction, status):
        self.progress_bar.set_fraction(fraction)
        self.update_status(status)
        
    def update_status(self, message):
        self.status_label.set_text(message)
        
    def on_transcription_complete(self, result):
        self.output_buffer.set_text(result)
        self.transcribe_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.update_status("Transcription complete")
        
    def on_transcription_finished(self, message):
        self.transcribe_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.update_status(message)

def main():
    app = WhisperTranscriber()
    return app.run(None)

if __name__ == "__main__":
    sys.exit(main())
