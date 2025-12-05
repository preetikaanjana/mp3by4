import os
import time
import textwrap
import threading
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip
import google.generativeai as genai
import traceback

# Try to import MediaPipe for advanced avatar processing
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not available (using basic avatar)")

# --- CONFIGURATION ---
GEMINI_KEY = "AIzaSyCVgb4hJFM9UNWiUI4GXXHZCGLv43HODNo" 

# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Gemini - try multiple model names
model = None
try:
    genai.configure(api_key=GEMINI_KEY)
    # Try different model names
    model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro', 'gemini-1.5-flash']
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            # Test with a simple prompt
            model.generate_content("test")
            print(f"✅ Gemini AI configured with model: {model_name}")
            break
        except Exception as e:
            continue
    if model is None:
        print("⚠️ Gemini AI not available (using fallback)")
except Exception as e:
    model = None
    print(f"⚠️ Gemini AI not available: {e} (using fallback)")

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def clean_old_files():
    for f in os.listdir(STATIC_DIR):
        if f.startswith("video_") or f.startswith("narration_"):
            try:
                os.remove(os.path.join(STATIC_DIR, f))
            except:
                pass

def generate_smart_summary(text):
    if model:
        try:
            prompt = (
                "You are a friendly narrator. Create a 4-sentence script summarizing this webpage. "
                "Do NOT mention 'AI' or 'Gemini'. Keep it engaging.\n\n"
                f"CONTENT: {text[:4000]}"
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini Error: {e}")
            pass
    return text[:600]

def create_avatar_video(script, audio_path, output_path):
    """
    Create an avatar video with animated character and text overlay.
    Uses MediaPipe if available for better avatar processing.
    """
    try:
        duration = 10
        if os.path.exists(audio_path):
            try:
                clip = AudioFileClip(audio_path)
                duration = clip.duration + 1
                clip.close()
            except Exception as e:
                print(f"⚠️ Could not read audio duration: {e}, using default 10s")
                duration = 10

        width, height = 1280, 720
        fps = 24
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_output = output_path.replace('.mp4', '_temp.mp4')
        
        # Ensure temp file doesn't exist
        if os.path.exists(temp_output):
            os.remove(temp_output)
            
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise Exception("Failed to open video writer")

        frames = int(duration * fps)
        lines = textwrap.wrap(script, width=60)
        
        # Background gradient colors
        bg_color_start = np.array([40, 44, 52])
        bg_color_end = np.array([60, 64, 72])

        for i in range(frames):
            # Create frame with gradient background
            img = np.zeros((height, width, 3), dtype=np.uint8)
            progress = i / max(frames, 1)
            bg_color = bg_color_start + (bg_color_end - bg_color_start) * progress
            img[:] = bg_color
            
            # Avatar center position
            cx, cy = width // 2, height // 2 - 50
            
            # Draw avatar head (circle)
            cv2.circle(img, (cx, cy), 100, (220, 220, 220), -1)
            cv2.circle(img, (cx, cy), 100, (180, 180, 180), 3)
            
            # Animated eyes - blinking
            blink_frame = i % 72
            if blink_frame < 5:  # Blink animation
                cv2.line(img, (cx-30, cy-20), (cx-10, cy-20), (0,0,0), 3)
                cv2.line(img, (cx+30, cy-20), (cx+50, cy-20), (0,0,0), 3)
            else:
                # Open eyes
                cv2.circle(img, (cx-20, cy-20), 10, (0,0,0), -1)
                cv2.circle(img, (cx+20, cy-20), 10, (0,0,0), -1)
                # Eye highlights
                cv2.circle(img, (cx-18, cy-22), 3, (255,255,255), -1)
                cv2.circle(img, (cx+22, cy-22), 3, (255,255,255), -1)

            # Animated mouth - talking animation
            # Ensure mouth_open is always positive and valid
            mouth_base = 10
            mouth_variation = 15
            mouth_open = mouth_base + int(mouth_variation * abs(np.sin(i * 0.5)))
            mouth_open = max(5, min(mouth_open, 25))  # Clamp between 5 and 25
            
            # Draw mouth ellipse - FIXED: ensure axes are valid
            mouth_center = (cx, cy + 40)
            axes = (25, mouth_open)
            cv2.ellipse(img, mouth_center, axes, 0, 0, 360, (200, 100, 100), -1)
            cv2.ellipse(img, mouth_center, axes, 0, 0, 360, (150, 80, 80), 2)

            # Text overlay at bottom
            current_line_idx = (i // (fps * 3)) % len(lines) if lines else 0
            current_line = lines[current_line_idx] if lines else ""
            
            # Draw text with background for readability
            if current_line:
                # Calculate text size
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2
                (text_width, text_height), baseline = cv2.getTextSize(current_line, font, font_scale, thickness)
                
                # Text position
                text_x = 50
                text_y = height - 50
                
                # Draw semi-transparent background for text
                overlay = img.copy()
                cv2.rectangle(overlay, (text_x - 10, text_y - text_height - 10), 
                            (text_x + text_width + 10, text_y + baseline + 10), 
                            (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
                
                # Draw text
                cv2.putText(img, current_line, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
            
            out.write(img)
            
            # Progress indicator
            if i % (fps * 2) == 0:
                progress_pct = int((i / frames) * 100)
                print(f"   📹 Rendering frame {i}/{frames} ({progress_pct}%)")

        out.release()
        print(f"   ✅ Video frames written to {temp_output}")

        # Combine video with audio
        if os.path.exists(audio_path) and os.path.exists(temp_output):
            try:
                print("   🎵 Combining video with audio...")
                v_clip = VideoFileClip(temp_output)
                a_clip = AudioFileClip(audio_path)
                
                # Ensure video duration matches audio
                if v_clip.duration < a_clip.duration:
                    # Loop video if needed
                    loops = int(np.ceil(a_clip.duration / v_clip.duration))
                    v_clip = VideoFileClip(temp_output).loop(duration=a_clip.duration)
                
                final = v_clip.set_audio(a_clip)
                final.write_videofile(output_path, codec='libx264', audio_codec='aac', 
                                     fps=fps, logger=None, verbose=False)
                v_clip.close()
                a_clip.close()
                final.close()
                
                # Clean up temp file
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                    
                # Verify output file exists
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Final video saved: {output_path} ({file_size} bytes)")
                    return True
                else:
                    raise Exception("Video file was not created")
                    
            except Exception as e:
                print(f"   ⚠️ Error combining audio: {e}")
                # Fallback: rename temp file if audio combination fails
                if os.path.exists(temp_output):
                    os.rename(temp_output, output_path)
                    return True
                return False
        else:
            # No audio, just rename temp file
            if os.path.exists(temp_output):
                os.rename(temp_output, output_path)
                return True
            return False
            
    except Exception as e:
        print(f"⚠️ Video Creation Error: {e}")
        traceback.print_exc()
        return False

@app.route('/process', methods=['POST'])
def process():
    print("\n📨 RECEIVED REQUEST FROM EXTENSION...")
    try:
        clean_old_files()
        data = request.json
        raw_text = data.get('content', '')
        
        unique_id = str(int(time.time()))
        
        print("1️⃣ Generating Summary...")
        script = generate_smart_summary(raw_text)
        
        print("2️⃣ Generating Audio (TTS)...")
        audio_filename = f"narration_{unique_id}.mp3"
        audio_path = os.path.join(STATIC_DIR, audio_filename)
        tts = gTTS(script, lang='en')
        tts.save(audio_path)
        print("   ✅ Audio Saved")
        
        print("3️⃣ Generating Video...")
        video_filename = f"video_{unique_id}.mp4"
        video_path = os.path.join(STATIC_DIR, video_filename)
        create_avatar_video(script, audio_path, video_path)
        print("   ✅ Video Saved")

        # Verify files exist before returning URLs
        video_exists = os.path.exists(video_path)
        audio_exists = os.path.exists(audio_path)
        
        if not video_exists:
            print(f"   ⚠️ Warning: Video file not found at {video_path}")
        if not audio_exists:
            print(f"   ⚠️ Warning: Audio file not found at {audio_path}")
        
        # Use 127.0.0.1 for consistency with extension
        base_url = "http://127.0.0.1:8080"
        
        return jsonify({
            "status": "success",
            "script": script,
            "video_url": f"{base_url}/static/{video_filename}" if video_exists else None,
            "audio_url": f"{base_url}/static/{audio_filename}" if audio_exists else None
        })

    except Exception as e:
        print("\n❌ CRITICAL SERVER CRASH ❌")
        print("--------------------------------------------------")
        traceback.print_exc()  # This prints the EXACT error details
        print("--------------------------------------------------")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with proper MIME types"""
    file_path = os.path.join(STATIC_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    # Set proper MIME types
    if filename.endswith('.mp4'):
        return send_from_directory(STATIC_DIR, filename, mimetype='video/mp4')
    elif filename.endswith('.mp3'):
        return send_from_directory(STATIC_DIR, filename, mimetype='audio/mpeg')
    else:
        return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    print(f"🚀 Debug Server running on http://localhost:8080")
    app.run(port=8080, debug=False)