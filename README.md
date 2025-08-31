# 🎬 MP3by4 - Web to Video Converter Chrome Extension

A Chrome extension that converts web pages into narrated videos with AI-generated summaries and text-to-speech.

## 🚀 Technologies Used

### Frontend (Chrome Extension)
- **HTML5/CSS3**: Modern, responsive popup interface with gradient backgrounds and animations
- **JavaScript (ES6+)**: 
  - Chrome Extension APIs for tab management and content extraction
  - Fetch API for server communication
  - DOM manipulation for dynamic UI updates
  - Async/await for asynchronous operations
- **Chrome Extension Manifest V3**: Modern extension architecture
- **CSS Animations**: Loading spinners, hover effects, and smooth transitions

### Backend (Python Server)
- **Flask**: Lightweight web framework for API endpoints
- **Flask-CORS**: Cross-origin resource sharing for Chrome extension communication
- **Google Gemini AI**: Advanced AI model for text summarization and content generation
- **BeautifulSoup4**: Web scraping and HTML parsing
- **pyttsx3**: Text-to-speech conversion (offline TTS engine)
- **Requests**: HTTP library for web content fetching

### Key Features
- **Web Content Extraction**: Extracts meaningful text from webpages
- **AI Summarization**: Uses Google Gemini AI to generate engaging summaries
- **Text-to-Speech**: Converts text to natural-sounding audio
- **Voice Selection**: Multiple voice types (professional, friendly, energetic, etc.)
- **Background Isolation**: Optional video background processing
- **Real-time Processing**: Live content processing and generation

## 📁 Project Structure

```
mp3by4/
├── extension/                 # Chrome Extension
│   ├── popup.html             # Main popup interface
│   ├── robust_popup.js        # Extension logic and API calls
│   ├── manifest.json          # Extension configuration
│   └── icons/                 # Extension icons
├── mp3by4/                    # Python Backend
│   ├── simple_working_server.py  # Main Flask server (port 8080)
│   ├── summarize.py           # AI summarization logic
│   ├── sentence_generate.py   # Text processing utilities
│   ├── tts.py                # Text-to-speech functionality
│   ├── text_extract.py       # Web scraping utilities
│   ├── config.py             # Configuration settings
│   ├── requirements.txt      # Python dependencies
│   ├── static/               # Generated audio/video files
│   └── output/               # Output directory
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### 1. Install Python Dependencies
```bash
cd mp3by4
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python simple_working_server.py
```
Server will run on: `http://localhost:8080`

### 3. Load Chrome Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder

### 4. Use the Extension
1. Navigate to any webpage
2. Click the MP3by4 extension icon
3. Choose voice type and options
4. Click "Convert to Video"

## 🎯 Core Technologies Breakdown

### Chrome Extension Architecture
- **Manifest V3**: Modern extension format with improved security
- **Content Scripts**: Extract text from web pages
- **Popup Interface**: User-friendly control panel
- **Background Scripts**: Handle extension lifecycle

### AI & Machine Learning
- **Google Gemini 1.5 Flash**: State-of-the-art AI model for text processing
- **Natural Language Processing**: Content analysis and summarization
- **Text Generation**: AI-powered narrative creation

### Audio Processing
- **pyttsx3**: Cross-platform text-to-speech
- **Audio Format Support**: MP3 generation and playback
- **Voice Customization**: Rate, volume, and voice type control

### Web Technologies
- **RESTful APIs**: JSON-based communication between extension and server
- **CORS Support**: Secure cross-origin requests
- **Async Processing**: Non-blocking content generation
- **Error Handling**: Robust error management and user feedback

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `mp3by4` directory:
```
GEMINI_KEY=your_gemini_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### API Keys Required
- **Google Gemini API**: Get free key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🎨 UI/UX Features

- **Modern Design**: Gradient backgrounds and smooth animations
- **Responsive Layout**: Works on different screen sizes
- **Loading States**: Visual feedback during processing
- **Error Handling**: User-friendly error messages
- **Voice Selection**: Multiple voice options with descriptions
- **Progress Indicators**: Real-time status updates

## 🚀 Performance Features

- **Efficient Text Extraction**: Smart content filtering
- **Caching**: Generated content storage
- **Background Processing**: Non-blocking operations
- **Memory Management**: Optimized resource usage
- **Error Recovery**: Graceful failure handling

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

