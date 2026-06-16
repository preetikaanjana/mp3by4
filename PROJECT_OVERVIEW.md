# 📚 MP3by4 Project - Complete File Structure & Technology Guide

## 🎯 Project Overview

**MP3by4** is a Chrome extension that converts web pages into narrated videos with AI-generated summaries, text-to-speech, and animated character videos with audio-reactive lip-sync.

---

## 📁 Project Structure

```
mp3by4/
├── extension/              # Chrome Extension (Frontend)
│   ├── manifest.json        # Extension configuration
│   ├── popup.html          # Extension UI interface
│   ├── robust_popup.js     # Extension logic & API calls
│   ├── background.js       # Service worker (Manifest V3)
│   └── icons/              # Extension icons
│
├── mp3by4/                 # Python Backend Server
│   ├── simple_working_server.py  # Main Flask server
│   ├── requirements.txt    # Python dependencies
│   ├── assets/            # Character image assets
│   │   ├── girl/
│   │   ├── robot/
│   │   └── news_anchor/
│   └── static/            # Generated videos/audio
│
├── README.md              # Project documentation
├── setup.bat              # Setup script
└── start_server.bat       # Server startup script
```

---

## 🔧 Frontend Files (Chrome Extension)

### 1. **`extension/manifest.json`**
**Purpose:** Chrome Extension configuration file (Manifest V3)

**Key Features:**
- Defines extension metadata (name, version, description)
- Declares permissions:
  - `activeTab`: Access to current browser tab
  - `scripting`: Inject scripts into web pages
  - `storage`: Store extension data
- Host permissions for localhost (8080, 5000)
- Configures popup UI and icons
- Content Security Policy for security

**Technologies:**
- Chrome Extension Manifest V3 API

---

### 2. **`extension/popup.html`**
**Purpose:** Main user interface for the extension popup

**Key Features:**
- Beautiful gradient UI with modern design
- Character selector (Girl, Robot, News Anchor)
- Convert button with loading animation
- Result display area for video and script
- Responsive styling with CSS animations

**Technologies:**
- HTML5
- CSS3 (Gradients, Flexbox, Animations)
- Vanilla JavaScript (no frameworks)

**Key Sections:**
- Header with title
- Character selector (radio buttons)
- Convert button
- Result container (video player, script display)

---

### 3. **`extension/robust_popup.js`**
**Purpose:** Main JavaScript logic for extension functionality

**Key Functions:**
1. **`getPageContent()`**
   - Extracts text from current webpage
   - Removes scripts, styles, nav, footer
   - Collects paragraphs and headers
   - Limits to 5000 characters

2. **`addStatus(msg, type)`**
   - Displays status messages (success/error/info)
   - Creates styled notification divs

3. **Main Click Handler**
   - Gets current tab
   - Injects content script to extract text
   - Sends POST request to Flask server
   - Displays video and script results
   - Handles errors gracefully

**Technologies:**
- Chrome Extension APIs:
  - `chrome.tabs.query()` - Get active tab
  - `chrome.scripting.executeScript()` - Inject scripts
- Fetch API - HTTP requests
- DOM Manipulation

**API Integration:**
- Sends POST to `http://127.0.0.1:8080/process`
- Includes `content`, `url`, and `character_name`
- Receives JSON with `video_url`, `audio_url`, `script`

---

### 4. **`extension/background.js`**
**Purpose:** Service worker for Manifest V3 (minimal implementation)

**Key Features:**
- Logs installation event
- Required by Manifest V3 architecture

**Technologies:**
- Chrome Extension Service Worker API

---

### 5. **`extension/icons/`**
**Purpose:** Extension icons in multiple sizes

**Files:**
- `icon16.png`, `icon32.png`, `icon48.png`, `icon128.png`
- `icon.svg` (vector version)

**Usage:** Displayed in Chrome toolbar and extension management page

---

## 🐍 Backend Files (Python Server)

### 6. **`mp3by4/simple_working_server.py`**
**Purpose:** Main Flask server handling all video generation logic

**Key Components:**

#### **A. Configuration & Setup**
- Flask app initialization
- CORS enabled for extension communication
- Gemini AI model setup with fallback
- Path configuration (static, assets directories)

#### **B. Core Functions:**

**1. `generate_smart_summary(text)`**
- Uses Google Gemini AI to create 4-sentence summaries
- Falls back to text truncation if AI fails
- **Technology:** `google-generativeai`

**2. `analyze_audio_amplitude(audio_path, duration, fps)`**
- Analyzes audio file to extract volume/amplitude per frame
- Uses RMS (Root Mean Square) calculation
- Returns normalized amplitude array (0-1)
- **Technology:** `moviepy` (AudioFileClip), `numpy`

**3. `load_character_images(character_name, width, height)`**
- Loads character sprites from `assets/{character_name}/`
- Loads `closed.png` and `open.png`
- Resizes images to video frame dimensions
- **Technology:** `opencv-python` (cv2.imread, cv2.resize)

**4. `overlay_image_with_alpha(base_img, overlay_img, x, y)`**
- Overlays character sprite onto video frame
- Handles alpha channel transparency (RGBA)
- Supports RGB, RGBA, and grayscale images
- **Technology:** `opencv-python`, `numpy`

**5. `create_avatar_video(script, audio_path, output_path, character_name)`**
- Main video generation function
- Creates video frames with character sprites
- Audio-reactive lip-sync (switches open/closed based on amplitude)
- Adds text overlay at bottom
- Combines video with audio
- **Technology:** `opencv-python`, `moviepy`, `numpy`

**6. `clean_old_files()`**
- Removes old generated videos/audio files
- Prevents disk space issues

#### **C. API Endpoints:**

**`POST /process`**
- Receives webpage content and character name
- Generates AI summary
- Creates TTS audio (MP3)
- Generates video with character animation
- Returns JSON with video/audio URLs

**`GET /static/<filename>`**
- Serves generated video and audio files
- Sets proper MIME types

**Technologies Used:**
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin requests
- **OpenCV (cv2)** - Video/image processing
- **NumPy** - Numerical operations
- **MoviePy** - Video editing, audio analysis
- **gTTS** - Text-to-speech
- **Google Generative AI** - Text summarization
- **MediaPipe** (optional) - Advanced avatar processing

---

### 7. **`mp3by4/requirements.txt`**
**Purpose:** Python package dependencies

**Key Libraries:**

**Core:**
- `Flask==3.0.3` - Web server framework
- `flask-cors==4.0.0` - CORS support

**AI & NLP:**
- `google-generativeai==0.3.2` - Gemini AI integration
- `gTTS==2.5.3` - Google Text-to-Speech

**Video/Audio Processing:**
- `opencv-python==4.12.0.88` - Computer vision, video generation
- `moviepy==1.0.3` - Video editing, audio analysis
- `imageio-ffmpeg==0.4.9` - FFmpeg wrapper for video codecs
- `mediapipe>=0.10.0` - Advanced media processing (optional)

**Data Processing:**
- `numpy<2.0.0` - Numerical arrays and operations
- `beautifulsoup4==4.12.3` - HTML parsing (if needed)

**Utilities:**
- `requests==2.32.3` - HTTP requests
- `python-dotenv==1.0.1` - Environment variables

---

### 8. **`mp3by4/assets/`**
**Purpose:** Character sprite images for video generation

**Structure:**
```
assets/
├── girl/
│   ├── closed.png    # Character with closed mouth
│   └── open.png      # Character with open mouth
├── robot/
│   ├── closed.png
│   └── open.png
└── news_anchor/
    ├── closed.png
    └── open.png
```

**Requirements:**
- PNG format (supports transparency)
- Recommended: 1080x1920 or 720x1280
- Auto-resized to 1280x720 for video

**Usage:** Loaded dynamically based on `character_name` parameter

---

### 9. **`mp3by4/static/`**
**Purpose:** Storage for generated files

**Contents:**
- `video_{timestamp}.mp4` - Generated videos
- `narration_{timestamp}.mp3` - Generated audio files
- Old files cleaned automatically

**Technology:** Flask static file serving

---

## 🛠️ Setup & Scripts

### 10. **`setup.bat`**
**Purpose:** Automated setup script for Windows

**Functions:**
- Checks Python installation
- Creates virtual environment
- Installs Python dependencies
- Provides next-step instructions

**Technology:** Windows Batch Scripting

---

### 11. **`start_server.bat`**
**Purpose:** Quick server startup script

**Functions:**
- Changes to mp3by4 directory
- Starts Flask server
- Keeps window open for logs

**Technology:** Windows Batch Scripting

---

### 12. **`README.md`**
**Purpose:** Project documentation

**Contents:**
- Installation instructions
- Usage guide
- Troubleshooting
- API documentation

---

## 🔄 Data Flow

```
1. User clicks extension icon
   ↓
2. Extension extracts webpage text
   ↓
3. POST request to Flask server (/process)
   ├─ Content: webpage text
   ├─ URL: page URL
   └─ Character: selected character name
   ↓
4. Server processes request:
   ├─ AI Summary (Gemini)
   ├─ TTS Audio (gTTS → MP3)
   └─ Video Generation:
      ├─ Load character images
      ├─ Analyze audio amplitude
      ├─ Generate frames (sprite animation)
      └─ Combine video + audio
   ↓
5. Server returns JSON:
   ├─ video_url
   ├─ audio_url
   └─ script
   ↓
6. Extension displays video and script
```

---

## 🎨 Video Generation Pipeline

1. **Audio Analysis**
   - Load audio file with MoviePy
   - Extract samples at native sample rate
   - Calculate RMS amplitude for each video frame
   - Normalize to 0-1 range

2. **Frame Generation**
   - Create gradient background
   - For each frame:
     - Check audio amplitude
     - If amplitude > threshold: use `open.png`
     - Else: use `closed.png`
     - Overlay character sprite
     - Add text overlay at bottom

3. **Video Assembly**
   - Write frames with OpenCV VideoWriter
   - Combine with audio using MoviePy
   - Export as MP4 (H.264 codec)

---

## 🔐 Security & Permissions

**Extension Permissions:**
- `activeTab` - Only accesses current tab (not all tabs)
- `scripting` - Required for content extraction
- `storage` - For extension settings (if needed)

**Server Security:**
- CORS enabled for localhost only
- Content Security Policy in manifest
- No external API keys exposed to frontend

---

## 📊 Technology Stack Summary

### Frontend:
- **HTML5/CSS3** - UI structure and styling
- **Vanilla JavaScript** - Extension logic
- **Chrome Extension APIs** - Browser integration

### Backend:
- **Python 3.8+** - Server language
- **Flask** - Web framework
- **OpenCV** - Video/image processing
- **MoviePy** - Video editing
- **NumPy** - Numerical operations
- **Google Gemini AI** - Text summarization
- **gTTS** - Text-to-speech

### Infrastructure:
- **FFmpeg** (via imageio-ffmpeg) - Video codecs
- **MediaPipe** (optional) - Advanced media processing

---

## 🎯 Key Features Implemented

1. ✅ **Web Content Extraction** - DOM parsing
2. ✅ **AI Summarization** - Gemini AI integration
3. ✅ **Text-to-Speech** - gTTS MP3 generation
4. ✅ **Sprite-Based Animation** - Character image loading
5. ✅ **Audio-Reactive Lip-Sync** - Amplitude-based animation
6. ✅ **Character Selection** - Multiple character support
7. ✅ **Video Generation** - OpenCV + MoviePy
8. ✅ **Error Handling** - Graceful fallbacks
9. ✅ **Modern UI** - Beautiful gradient interface

---

## 🚀 Future Enhancements

Potential improvements:
- More character options
- Custom background images
- Multiple language support
- Video quality settings
- Batch processing
- Cloud storage integration

---

This project demonstrates a full-stack application combining browser extensions, web APIs, AI integration, and multimedia processing!

