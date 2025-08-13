#!/usr/bin/env python3
"""
YouTube Transcript Extractor with Whisper AI
Real-time progress tracking and modern UI
"""
import sys
import os
import webbrowser
import threading
import time
import subprocess
import tempfile
import re
import json
import shutil
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whisper_transcript_app_2025'
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=False,  # Disable Socket.IO debug logs in production
    engineio_logger=False,  # Disable engine.io debug logs
    ping_timeout=60,  # Longer timeout for cloud deployments
    ping_interval=25   # More frequent pings for reliable connection
)


def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_disk_usage():
    """Get available disk space for monitoring"""
    try:
        total, used, free = shutil.disk_usage('/')
        free_mb = free / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        return free_mb, total_mb
    except:
        return None, None

class ProgressHook:
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.download_progress = 0
        
    def __call__(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.download_progress = percent
                self.socketio.emit('progress', {
                    'message': 'Downloading audio...',
                    'detail': f"Downloaded {d['downloaded_bytes']:,} of {d['total_bytes']:,} bytes",
                    'percentage': percent,
                    'phase': 'download'
                })
            elif '_percent_str' in d:
                # Fallback to yt-dlp's percent string
                percent_str = d['_percent_str'].strip()
                if '%' in percent_str:
                    try:
                        percent = float(percent_str.replace('%', ''))
                        self.download_progress = percent
                        self.socketio.emit('progress', {
                            'message': 'Downloading audio...',
                            'detail': f"Progress: {percent_str}",
                            'percentage': percent,
                            'phase': 'download'
                        })
                    except:
                        pass
        elif d['status'] == 'finished':
            self.socketio.emit('progress', {
                'message': 'Download complete!',
                'detail': 'Preparing for transcription...',
                'percentage': 100,
                'phase': 'download'
            })

def download_and_transcribe_with_progress(youtube_url, socketio_instance):
    """Download video and transcribe with Whisper with progress tracking"""
    print(f"Processing: {youtube_url}")
    
    # Emit initial progress
    socketio_instance.emit('progress', {
        'message': 'Initializing download...',
        'detail': 'Setting up yt-dlp',
        'percentage': 0,
        'phase': 'download'
    })
    
    # Check available disk space
    free_mb, total_mb = get_disk_usage()
    if free_mb and free_mb < 100:  # Less than 100MB free
        raise Exception(f"Insufficient disk space: {free_mb:.0f}MB available")
    
    if free_mb:
        print(f"Disk space: {free_mb:.0f}MB free of {total_mb:.0f}MB total")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Download audio with progress tracking
            progress_hook = ProgressHook(socketio_instance)
            
            import yt_dlp
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': f'{temp_dir}/audio.%(ext)s',
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Find downloaded file
            files = [f for f in os.listdir(temp_dir) if f.startswith('audio.')]
            if not files:
                raise Exception("No audio file found after download")
            
            audio_file = os.path.join(temp_dir, files[0])
            file_size = os.path.getsize(audio_file)
            file_size_mb = file_size / (1024 * 1024)
            print(f"Downloaded: {files[0]} ({file_size_mb:.1f}MB)")
            
            # Log file info for monitoring
            socketio_instance.emit('progress', {
                'message': 'Download complete!',
                'detail': f'Audio file: {file_size_mb:.1f}MB - preparing for transcription',
                'percentage': 100,
                'phase': 'download'
            })
            
            # Start transcription phase
            socketio_instance.emit('progress', {
                'message': 'Starting transcription...',
                'detail': 'Loading Whisper model',
                'percentage': 0,
                'phase': 'transcribe'
            })
            
            # Transcribe with faster-whisper
            try:
                from faster_whisper import WhisperModel
                
                socketio_instance.emit('progress', {
                    'message': 'Loading Whisper model...',
                    'detail': 'Initializing base model',
                    'percentage': 10,
                    'phase': 'transcribe'
                })
                
                model = WhisperModel("base", device="cpu", compute_type="int8")
                
                socketio_instance.emit('progress', {
                    'message': 'Transcribing audio...',
                    'detail': 'Processing speech recognition',
                    'percentage': 30,
                    'phase': 'transcribe'
                })
                
                segments, info = model.transcribe(audio_file, language="en")
                
                socketio_instance.emit('progress', {
                    'message': 'Processing results...',
                    'detail': f"Detected language: {info.language} (confidence: {info.language_probability:.2f})",
                    'percentage': 80,
                    'phase': 'transcribe'
                })
                
                transcript_parts = []
                for i, segment in enumerate(segments):
                    transcript_parts.append(segment.text)
                    # Update progress during segment processing
                    if i % 10 == 0:  # Update every 10 segments
                        socketio_instance.emit('progress', {
                            'message': 'Assembling transcript...',
                            'detail': f"Processing segment {i + 1}",
                            'percentage': 80 + (i * 15 / max(1, len(transcript_parts))),
                            'phase': 'transcribe'
                        })
                
                transcript = " ".join(transcript_parts).strip()
                
                socketio_instance.emit('progress', {
                    'message': 'Transcription complete!',
                    'detail': f"Generated {len(transcript)} characters",
                    'percentage': 100,
                    'phase': 'transcribe'
                })
                
                return transcript
                
            except ImportError:
                raise Exception("faster-whisper not installed. Please install it first.")
            except Exception as e:
                raise Exception(f"Transcription failed: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_extraction')
def handle_extraction(data):
    url = data.get('url')
    
    if not url:
        emit('transcription_error', {'error': 'No URL provided'})
        return
    
    # Validate YouTube URL
    video_id = extract_video_id(url)
    if not video_id:
        emit('transcription_error', {'error': 'Invalid YouTube URL'})
        return
    
    def extraction_task():
        try:
            transcript = download_and_transcribe_with_progress(url, socketio)
            if not transcript:
                socketio.emit('transcription_error', {'error': 'No transcript generated'})
                return
            
            socketio.emit('transcription_complete', {'transcript': transcript})
            
        except Exception as e:
            socketio.emit('transcription_error', {'error': str(e)})
    
    # Run extraction in background thread
    thread = threading.Thread(target=extraction_task)
    thread.daemon = True
    thread.start()

def open_browser(host='127.0.0.1', port=5000):
    time.sleep(1.5)
    webbrowser.open(f'http://{host}:{port}')

def main():
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print("🎥 YouTube Transcript Extractor - Whisper AI Edition")
    print("=" * 60)
    print(f"Server running at http://{host}:{port}")
    print("Features: Real-time progress • yt-dlp + Whisper • Copy to clipboard")
    print("=" * 60)
    
    # Only open browser in local development
    if host == '127.0.0.1':
        print("Opening browser... Close this window to quit.")
        threading.Thread(target=lambda: open_browser(host, port), daemon=True).start()
    
    try:
        # Use 0.0.0.0 for production deployments
        if host != '127.0.0.1':
            host = '0.0.0.0'
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nApplication stopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()