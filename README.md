# 🎬 MP3by4 - Web to Video Converter Chrome Extension

A Chrome extension that converts web pages into narrated videos with AI-generated summaries, text-to-speech, and animated avatar videos.

## ✨ Features

- **Web Content Extraction**: Automatically extracts meaningful text from any webpage
- **AI Summarization**: Uses Google Gemini AI to generate engaging 4-sentence summaries
- **Text-to-Speech**: Converts summaries to natural-sounding MP3 audio using gTTS
- **Animated Video Generation**: Creates videos with animated avatar, text overlays, and synchronized audio
- **Real-time Processing**: Live content processing and video generation
- **Modern UI**: Beautiful gradient interface with smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Python 3.13 recommended)
- Chrome or Edge browser
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or download this repository**

2. **Set up Python virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Mac/Linux
   ```

3. **Install Python dependencies**:
   ```bash
   cd mp3by4
   pip install -r requirements.txt
   ```

   **Note**: If you encounter NumPy compatibility issues with Python 3.13, the requirements.txt already specifies compatible versions.

4. **Configure Gemini API Key**:
   
   Edit `mp3by4/simple_working_server.py` and replace the `GEMINI_KEY` value (line 15) with your API key:
   ```python
   GEMINI_KEY = "your_api_key_here"
   ```

5. **Start the server**:
   ```bash
   cd mp3by4
   python simple_working_server.py
   ```
   
   Server will run on: `http://127.0.0.1:8080`

6. **Load the Chrome Extension**:
   - Open Chrome/Edge and navigate to `chrome://extensions/` (or `edge://extensions/`)
   - Enable **"Developer mode"** (toggle in top-right)
   - Click **"Load unpacked"**
   - Select the `extension` folder from this project

### Usage

1. Navigate to any webpage you want to convert
2. Click the **MP3by4** extension icon in your browser toolbar
3. Click **"🚀 Convert to Video"**
4. Wait for processing (summary generation → audio creation → video rendering)
5. Watch your generated video with AI narration!

## 📁 Project Structure

```
mp3by4/
├── extension/                    # Chrome Extension
│   ├── popup.html               # Main popup interface
│   ├── robust_popup.js          # Extension logic and API calls
│   ├── background.js            # Background service worker
│   ├── manifest.json            # Extension configuration (Manifest V3)
│   └── icons/                   # Extension icons
│
├── mp3by4/                      # Python Backend
│   ├── simple_working_server.py # Main Flask server (port 8080)
│   ├── requirements.txt        # Python dependencies
│   └── static/                 # Generated videos and audio files
│
├── start_server.bat            # Windows script to start server
├── setup.bat                   # Windows setup script
└── README.md                   # This file
```

## 🛠️ Technologies Used

### Frontend (Chrome Extension)
- **HTML5/CSS3**: Modern, responsive popup interface with gradient backgrounds
- **JavaScript (ES6+)**: 
  - Chrome Extension APIs (Manifest V3)
  - Content script injection for text extraction
  - Fetch API for server communication
- **Chrome Extension Manifest V3**: Modern extension architecture

### Backend (Python Server)
- **Flask**: Lightweight web framework for API endpoints
- **Flask-CORS**: Cross-origin resource sharing
- **Google Gemini AI**: AI model for text summarization
- **gTTS (Google Text-to-Speech)**: Text-to-speech conversion
- **OpenCV**: Video generation with animated avatar
- **MoviePy**: Video editing and audio synchronization
- **NumPy**: Numerical operations for video processing

## 🔧 API Endpoints

### `POST /process`
Processes webpage content and generates video.

**Request:**
```json
{
  "content": "extracted webpage text",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "script": "AI-generated summary script",
  "video_url": "http://127.0.0.1:8080/static/video_1234567890.mp4",
  "audio_url": "http://127.0.0.1:8080/static/narration_1234567890.mp3"
}
```

### `GET /static/<filename>`
Serves generated video and audio files.

## 🎨 Video Generation Details

The video generation pipeline:

1. **Text Extraction**: Extracts main content from webpage (paragraphs, headers)
2. **AI Summarization**: Uses Gemini AI to create a 4-sentence engaging summary
3. **Audio Generation**: Converts summary to MP3 using gTTS
4. **Video Creation**: 
   - Creates animated avatar (blinking eyes, talking mouth)
   - Adds text overlay at bottom
   - Synchronizes audio with video
   - Outputs MP4 file with H.264 codec

## ⚙️ Configuration

### Server Configuration
Edit `mp3by4/simple_working_server.py`:
- `GEMINI_KEY`: Your Google Gemini API key
- `PORT`: Server port (default: 8080)

### Extension Configuration
Edit `extension/manifest.json`:
- `host_permissions`: Server URLs (default: `http://localhost:8080/*`)

## 🐛 Troubleshooting

### Server won't start
- **NumPy/OpenCV errors**: Make sure you're using compatible versions. For Python 3.13, use `opencv-python-headless` or latest `opencv-python`.
- **Missing modules**: Run `pip install -r mp3by4/requirements.txt`

### Extension can't connect to server
- Make sure the server is running on port 8080
- Check that `host_permissions` in `manifest.json` includes your server URL
- Try using `127.0.0.1` instead of `localhost`

### Video generation fails
- Check server console for error messages
- Ensure audio file was generated successfully
- Verify OpenCV is installed correctly: `python -c "import cv2; print(cv2.__version__)"`

### Gemini API errors
- Verify your API key is correct
- Check your API quota/limits
- The server will fall back to simple text truncation if Gemini fails

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 🙏 Acknowledgments

- Google Gemini AI for text summarization
- OpenCV for video processing
- MoviePy for video editing
- gTTS for text-to-speech
