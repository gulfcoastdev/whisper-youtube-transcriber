# 🎥 YouTube Transcript Extractor - Whisper AI

## Quickstart

### Install dependencies
```bash
pip install -r requirements.txt
```

### Requirements

- Python 3.8+

### Troubleshooting

#### Installation Issues

If installation fails, try:
```bash
# Error encountered: Collecting flask==2.3.3 (from -r requirements.txt (line 1))
  Using cached flask-2.3.3-py3-none-any.whl (96 kB)
Collecting flask-socketio==5.5.1 (from -r requirements.txt (line 2))
  Downloading Flask...
```



A modern, real-time YouTube transcript extractor powered by yt-dlp and OpenAI Whisper AI.

## ✨ Features

- **🚀 Real-time Progress Tracking** - Live progress bars for download and transcription
- **🎤 AI-Powered Transcription** - OpenAI Whisper for high-quality speech recognition
- **📥 Smart Download** - Audio-only extraction for faster processing
- **📋 Copy to Clipboard** - One-click transcript copying
- **🌐 Modern Web UI** - Beautiful, responsive interface
- **⚡ WebSocket Updates** - Real-time progress without page refresh
- **🔄 Phase Indicators** - Visual progress through Download → Transcribe → Complete

## 🚀 Quick Start

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd whisper-youtube-transcriber
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open browser:** http://127.0.0.1:5000

### Cloud Deployment

#### Heroku
```bash
heroku create your-app-name
git push heroku main
```

#### Render
- Connect your GitHub repository
- Render will auto-detect the `render.yaml` file
- Automatic deployment on git push

#### Railway
- Connect GitHub repo
- Railway auto-detects Flask apps
- Environment variables set automatically

## 🛠️ Technical Stack

- **Backend:** Flask + Socket.IO for real-time communication
- **AI:** OpenAI Whisper (faster-whisper implementation)
- **Downloader:** yt-dlp for reliable YouTube audio extraction
- **Frontend:** Modern HTML5 + CSS3 + JavaScript
- **Real-time:** WebSocket for live progress updates

## 📋 Requirements

- Python 3.11+
- ~2GB RAM (for Whisper model)
- Internet connection for YouTube access

## 🎯 How It Works

1. **URL Input** - Paste any YouTube URL
2. **Download Phase** - Extract audio using yt-dlp with progress tracking
3. **Transcription Phase** - Process audio through Whisper AI
4. **Results** - View transcript with copy-to-clipboard functionality

## 🔧 Configuration

### Environment Variables

- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 127.0.0.1)
- `PYTHON_VERSION` - Python version for deployment (3.11)

### Whisper Models

The app uses the "base" Whisper model by default. You can modify this in `app.py`:

```python
model = WhisperModel("base", device="cpu", compute_type="int8")
```

Available models:
- `tiny` - Fastest, least accurate
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - Higher accuracy
- `large` - Best accuracy, slowest

## 🎨 UI Features

- **Progress Visualization** - Animated progress bars
- **Phase Indicators** - 📥 Download → 🎤 Transcribe → ✅ Complete
- **Real-time Updates** - Live file sizes, percentages, confidence scores
- **Copy Button** - One-click clipboard copying with visual feedback
- **Error Handling** - Graceful error messages and recovery

## 🚀 Performance

- **Audio-only download** - 10x faster than full video
- **Efficient processing** - Optimized Whisper implementation
- **Progress tracking** - Real-time feedback for user experience
- **Background processing** - Non-blocking operations

## 📱 Browser Support

- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers supported

## 🔒 Privacy

- **No data storage** - Transcripts processed locally
- **Temporary files** - Audio files automatically deleted
- **No tracking** - No analytics or user data collection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- yt-dlp for YouTube audio extraction
- Flask-SocketIO for real-time updates

---

**Built with ❤️ for accurate, fast YouTube transcription**