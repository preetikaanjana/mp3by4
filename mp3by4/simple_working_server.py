from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import pyttsx3
import base64

app = Flask(__name__)
CORS(app)

# Configure Gemini AI
GEMINI_KEY = "AIzaSyCVgb4hJFM9UNWiUI4GXXHZCGLv43HODNo"
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini AI configured successfully")
except Exception as e:
    print(f"⚠️ Gemini AI configuration failed: {e}")
    model = None

def extract_text_from_webpage(url):
    """Extract the actual story content from webpage"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Extract meaningful story content
        story_elements = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div']):
            text = element.get_text(strip=True)
            if text and len(text) > 30:  # Only meaningful content
                story_elements.append(text)
        
        # Join the story content
        full_story = '\n\n'.join(story_elements[:15])  # First 15 meaningful elements
        return full_story
        
    except Exception as e:
        print(f"Error extracting text: {e}")
        return f"Error extracting content: {str(e)}"

def generate_ai_summary(text, url):
    """Generate a brief summary for display"""
    if not model:
        return "AI summarization not available."
    
    try:
        prompt = f"Summarize this story in 2-3 engaging sentences: {text[:1500]}..."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Story about {url} with {len(text)} characters of content."

def convert_text_to_speech(full_story):
    """Convert the FULL STORY to speech, not just summary"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        static_folder = 'static'
        os.makedirs(static_folder, exist_ok=True)
        
        # Use the FULL STORY for TTS
        output_path = os.path.join(static_folder, 'full_story.mp3')
        engine.save_to_file(full_story, output_path)
        engine.runAndWait()
        
        return '/static/full_story.mp3'
        
    except Exception as e:
        print(f"Text-to-speech conversion failed: {e}")
        return None

def create_story_content(text, summary):
    """Create story content files"""
    try:
        static_folder = 'static'
        os.makedirs(static_folder, exist_ok=True)
        
        # Create a detailed story file
        story_file = os.path.join(static_folder, 'story_content.txt')
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write("🎬 MP3by4 STORY CONTENT\n")
            f.write("=" * 50 + "\n\n")
            f.write("📖 FULL STORY:\n")
            f.write("-" * 30 + "\n")
            f.write(text[:2000])  # First 2000 characters
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("🤖 AI SUMMARY:\n")
            f.write("-" * 30 + "\n")
            f.write(summary)
            f.write("\n\n" + "=" * 50 + "\n")
            f.write(f"📊 Story Statistics:\n")
            f.write(f"- Total Characters: {len(text)}\n")
            f.write(f"- Summary Length: {len(summary)}\n")
            f.write(f"- Content Type: Webpage Story\n")
        
        return '/static/story_content.txt'
        
    except Exception as e:
        print(f"Content creation failed: {e}")
        return None

@app.route('/')
def home():
    return jsonify({
        "message": "🎬 MP3by4 Working Story Server",
        "status": "active",
        "features": ["Full story TTS", "Story content files", "AI summaries"],
        "endpoints": ["/", "/generate_narration", "/health"]
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "ai_status": "enabled" if model else "demo_mode",
        "server": "Working Story Server"
    })

@app.route('/generate_narration', methods=['POST'])
def generate_narration():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        print(f"🔄 Processing URL: {url}")
        
        # Extract the FULL STORY text
        full_story = extract_text_from_webpage(url)
        print(f"📖 Extracted {len(full_story)} characters of story")
        
        # Generate AI summary for display
        summary = generate_ai_summary(full_story, url)
        print(f"🤖 Generated summary: {len(summary)} characters")
        
        # Create TTS from the FULL STORY (not summary!)
        print("🎙️ Converting FULL STORY to speech...")
        mp3_url = convert_text_to_speech(full_story)
        
        # Create story content file
        print("📄 Creating story content file...")
        content_url = create_story_content(full_story, summary)
        
        response = {
            "status": "success",
            "url": url,
            "extracted_text": full_story[:300] + "..." if len(full_story) > 300 else full_story,
            "narrative": summary,
            "mp3_url": mp3_url,
            "video_url": content_url,  # For now, this is the content file
            "ai_enabled": model is not None,
            "notes": f"📝 Story Summary:\n{summary}\n\n📖 Full Story Length: {len(full_story)} characters\n🎧 Audio: FULL STORY narration (not just summary)\n📄 Content: Detailed story file created"
        }
        
        print("✅ Successfully generated narration and content")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error in generate_narration: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🚀 Starting MP3by4 Working Story Server...")
    print("🎧 TTS reads the FULL STORY, not just summaries!")
    print("📄 Creates detailed story content files!")
    print(f"🌐 Server will be available at: http://localhost:8080")
    
    try:
        app.run(host='127.0.0.1', port=8080, debug=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
