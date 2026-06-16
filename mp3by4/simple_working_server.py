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
import requests
from bs4 import BeautifulSoup

# Try to import MediaPipe for advanced avatar processing
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available (using basic avatar)")

# --- CONFIGURATION ---
GEMINI_KEY = "AIzaSyCVgb4hJFM9UNWiUI4GXXHZCGLv43HODNo" 

# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Gemini - try multiple model names
model = None
if GEMINI_KEY == "AIzaSyCVgb4hJFM9UNWiUI4GXXHZCGLv43HODNo" or not GEMINI_KEY or "api_key" in GEMINI_KEY.lower():
    print("⚠️ WARNING: Default deactivated or placeholder Gemini API key is configured.")
    print("   The server will run in Heuristic Fallback mode (no API calls).")
else:
    try:
        genai.configure(api_key=GEMINI_KEY)
        # Try different model names
        model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro', 'gemini-1.5-flash']
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"Gemini AI configured with model: {model_name}")
                break
            except Exception as e:
                print(f"Model {model_name} initialization failed: {e}")
                continue
        if model is None:
            print("⚠️ Gemini AI not available (using fallback)")
    except Exception as e:
        model = None
        print(f"⚠️ Gemini AI configuration failed: {e} (using fallback)")
        print("   The server will use simple text truncation instead of AI summarization.")

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

def clean_old_files():
    for f in os.listdir(STATIC_DIR):
        if f.startswith("video_") or f.startswith("narration_"):
            try:
                os.remove(os.path.join(STATIC_DIR, f))
            except:
                pass

def scrape_webpage_content(url):
    """
    Fetch webpage HTML and extract main text content.
    Strips scripts, styles, nav, footer, etc.
    """
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print(f"🕸️ Scraping webpage content from URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 'iframe', 'noscript']):
            element.decompose()
            
        # Get paragraphs and headers
        text_parts = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
            text = element.get_text().strip()
            if len(text) > 30:
                text_parts.append(text)
                
        extracted_text = "\n".join(text_parts)
        print(f"   ✅ Successfully scraped {len(extracted_text)} characters")
        return extracted_text[:5000] # Limit to 5000 chars
    except Exception as e:
        print(f"⚠️ Scraping failed: {e}")
        return ""

def generate_smart_summary_and_notes(text, character_name="girl"):
    """
    Generate a 4-sentence summary script and bulleted takeaway notes
    customized to the narrator's sitcom persona.
    """
    if model:
        try:
            # Determine persona instructions
            persona_instruction = ""
            if character_name == "robot":
                persona_instruction = (
                    "You are Sheldon Cooper from Big Bang Theory. Write a highly logical, "
                    "slightly pedantic, and precise summary script. Use phrases like 'Bazinga!' "
                    "or 'Fascinating' or 'According to physics...'. Make it sound exactly like Sheldon."
                )
            elif character_name == "news_anchor":
                persona_instruction = (
                    "You are Michael Scott from The Office. Write a dramatic, energetic, and "
                    "slightly chaotic summary script. Use phrases like 'That's what she said!', "
                    "'Alright, listen up!', or 'This is a big deal, people!'. Make it sound exactly like Michael."
                )
            else:  # 'girl' or fallback
                persona_instruction = (
                    "You are Rachel Green from Friends. Write an enthusiastic, friendly, and "
                    "slightly gossipy summary script. Use phrases like 'Oh my god!', 'I know!', "
                    "or 'Could this BE any more...'. Make it sound exactly like Rachel."
                )

            prompt = (
                f"{persona_instruction}\n\n"
                "Your task is to analyze the webpage content below and generate two parts:\n"
                "1. A 4-sentence narration script. It must be engaging, fit your persona perfectly, "
                "and explain the key essence of the text. Do not mention 'AI' or 'Gemini'.\n"
                "2. A neat bulleted list of 3-4 'Ready-Made Notes' (key takeaways) summarizing the page facts.\n\n"
                "Format your output exactly as follows with the headers:\n"
                "---SCRIPT---\n"
                "[Your 4-sentence narration script here]\n"
                "---NOTES---\n"
                "- [Takeaway 1]\n"
                "- [Takeaway 2]\n"
                "...\n\n"
                f"CONTENT TO SUMMARIZE:\n{text[:4000]}"
            )
            response = model.generate_content(prompt, request_options={"timeout": 5.0})
            if response and hasattr(response, 'text'):
                return response.text.strip()
            else:
                print("⚠️ Gemini returned empty response, using fallback")
                return None
        except Exception as e:
            print(f"⚠️ Gemini Error: {e}")
            traceback.print_exc()
            return None
    return None


def analyze_audio_amplitude(audio_path, duration, fps):
    """
    Analyze audio file to get amplitude (volume) for each frame.
    Returns a list of amplitude values, one per frame.
    """
    try:
        if not os.path.exists(audio_path):
            print(f"⚠️ Audio file not found: {audio_path}")
            return None
        
        audio_clip = AudioFileClip(audio_path)
        
        # Get audio samples at the audio's native sample rate
        audio_array = audio_clip.to_soundarray()
        audio_sample_rate = audio_clip.fps  # Audio sample rate (typically 44100 Hz)
        
        # Calculate RMS (Root Mean Square) amplitude for each video frame
        num_frames = int(duration * fps)
        frame_duration = duration / num_frames
        amplitudes = []
        
        for i in range(num_frames):
            start_time = i * frame_duration
            end_time = min((i + 1) * frame_duration, duration)
            
            # Convert time to sample indices based on audio sample rate
            start_sample = int(start_time * audio_sample_rate)
            end_sample = int(end_time * audio_sample_rate)
            
            if start_sample < len(audio_array):
                # Get audio chunk for this frame
                chunk = audio_array[start_sample:end_sample]
                
                # Calculate RMS amplitude
                if len(chunk) > 0:
                    try:
                        # Handle mono or stereo audio
                        if len(chunk.shape) == 2 and chunk.shape[1] > 1:
                            # Stereo: average channels (axis=1 means average across channels)
                            chunk = np.mean(chunk, axis=1)
                        # Calculate RMS (Root Mean Square)
                        # Ensure chunk is 1D array
                        chunk_flat = chunk.flatten()
                        rms = np.sqrt(np.mean(chunk_flat ** 2))
                        amplitudes.append(float(rms))
                    except Exception as e:
                        # Fallback: use absolute mean
                        amplitudes.append(float(np.mean(np.abs(chunk))))
                else:
                    amplitudes.append(0.0)
            else:
                amplitudes.append(0.0)
        
        audio_clip.close()
        
        # Normalize amplitudes to 0-1 range
        if amplitudes:
            max_amp = max(amplitudes) if max(amplitudes) > 0 else 1.0
            amplitudes = [a / max_amp for a in amplitudes]
        
        return amplitudes
        
    except Exception as e:
        print(f"⚠️ Error analyzing audio amplitude: {e}")
        traceback.print_exc()
        return None

def load_character_images(character_name, width, height):
    """
    Load character images (closed.png and open.png) from assets folder.
    Returns tuple (closed_img, open_img) or (None, None) if not found.
    """
    try:
        character_dir = os.path.join(ASSETS_DIR, character_name)
        
        closed_path = os.path.join(character_dir, 'closed.png')
        open_path = os.path.join(character_dir, 'open.png')
        
        closed_img = None
        open_img = None
        
        target_h = 520
        
        if os.path.exists(closed_path):
            closed_img = cv2.imread(closed_path, cv2.IMREAD_UNCHANGED)
            if closed_img is not None:
                h_orig, w_orig = closed_img.shape[:2]
                target_w = int(w_orig * (target_h / h_orig))
                closed_img = cv2.resize(closed_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                print(f"   ✅ Loaded character closed image: {closed_path}")
        else:
            print(f"   ⚠️ Character closed image not found: {closed_path}")
        
        if os.path.exists(open_path):
            open_img = cv2.imread(open_path, cv2.IMREAD_UNCHANGED)
            if open_img is not None:
                h_orig, w_orig = open_img.shape[:2]
                target_w = int(w_orig * (target_h / h_orig))
                open_img = cv2.resize(open_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                print(f"   ✅ Loaded character open image: {open_path}")
        else:
            print(f"   ⚠️ Character open image not found: {open_path}")
        
        return closed_img, open_img
        
    except Exception as e:
        print(f"⚠️ Error loading character images: {e}")
        traceback.print_exc()
        return None, None

def overlay_image_with_alpha(base_img, overlay_img, x, y):
    """
    Overlay an image with alpha channel onto a base image.
    """
    if overlay_img is None:
        return base_img
    
    h, w = overlay_img.shape[:2]
    base_h, base_w = base_img.shape[:2]
    
    # Calculate the region to overlay
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(base_w, x + w)
    y2 = min(base_h, y + h)
    
    # Calculate the region from overlay image
    ox1 = max(0, -x)
    oy1 = max(0, -y)
    ox2 = ox1 + (x2 - x1)
    oy2 = oy1 + (y2 - y1)
    
    if x2 <= x1 or y2 <= y1:
        return base_img
    
    # Extract the region from base and overlay
    try:
        base_region = base_img[y1:y2, x1:x2].copy()
        overlay_region = overlay_img[oy1:oy2, ox1:ox2].copy()
    except Exception as e:
        print(f"⚠️ Error extracting regions in overlay: {e}")
        return base_img
    
    # Handle alpha channel
    try:
        if len(overlay_region.shape) == 3:
            if overlay_region.shape[2] == 4:  # Has alpha channel (RGBA)
                alpha = overlay_region[:, :, 3:4] / 255.0
                overlay_rgb = overlay_region[:, :, :3]
                base_region = (base_region * (1 - alpha) + overlay_rgb * alpha).astype(np.uint8)
            elif overlay_region.shape[2] == 3:  # RGB without alpha
                # Direct overlay for RGB images
                base_region = overlay_region
            else:
                # Unexpected channel count, convert to RGB
                base_region = cv2.cvtColor(overlay_region, cv2.COLOR_GRAY2BGR) if len(overlay_region.shape) == 2 else overlay_region[:, :, :3]
        else:
            # Grayscale - convert to RGB
            overlay_region = cv2.cvtColor(overlay_region, cv2.COLOR_GRAY2BGR)
            base_region = overlay_region
    except Exception as e:
        print(f"⚠️ Error handling alpha channel: {e}")
        # Fallback: direct copy
        try:
            if len(overlay_region.shape) == 3 and overlay_region.shape[2] >= 3:
                base_region = overlay_region[:, :, :3]
            else:
                base_region = overlay_region
        except:
            return base_img
    
    # Assign the modified region back to the base image
    try:
        base_img[y1:y2, x1:x2] = base_region
    except Exception as e:
        print(f"⚠️ Error assigning region back: {e}")
    
    return base_img

def create_avatar_video(script, audio_path, output_path, character_name=None):
    """
    Create an avatar video with sprite-based character animation and text overlay.
    Uses audio-reactive lip-sync animation based on audio amplitude.
    
    Args:
        script: Text script to display
        audio_path: Path to audio file
        output_path: Path to save video
        character_name: Name of character folder in assets/ (e.g., 'character1')
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
        
        # Load character images if character_name is provided
        closed_img = None
        open_img = None
        use_sprites = False
        
        if character_name:
            print(f"   🎭 Loading character: {character_name}")
            closed_img, open_img = load_character_images(character_name, width, height)
            if closed_img is not None and open_img is not None:
                use_sprites = True
                print(f"   ✅ Using sprite-based animation")
            else:
                print(f"   ⚠️ Character images not found, falling back to geometric shapes")
        
        # Analyze audio amplitude for lip-sync
        print(f"   🎵 Analyzing audio amplitude for lip-sync...")
        amplitudes = analyze_audio_amplitude(audio_path, duration, fps)
        
        # Set threshold for mouth open/closed (adjustable)
        amplitude_threshold = 0.15  # Lower threshold = more sensitive
        
        if amplitudes is None:
            print(f"   ⚠️ Could not analyze audio, using time-based animation")
            amplitudes = [abs(np.sin(i * 0.3)) for i in range(frames)]  # Fallback
        
        # Background gradient colors (improved)
        bg_color_start = np.array([30, 40, 60])  # Dark blue-gray
        bg_color_end = np.array([50, 60, 80])    # Lighter blue-gray

        for i in range(frames):
            # Create frame with gradient background
            img = np.zeros((height, width, 3), dtype=np.uint8)
            progress = i / max(frames, 1)
            bg_color = bg_color_start + (bg_color_end - bg_color_start) * progress
            img[:] = bg_color
            
            # Overlay character sprite or draw geometric shapes
            if use_sprites:
                # Use sprite-based animation
                current_amplitude = amplitudes[i] if i < len(amplitudes) else 0.0
                
                # Choose sprite based on audio amplitude
                if current_amplitude > amplitude_threshold:
                    # Mouth open (talking)
                    character_sprite = open_img
                else:
                    # Mouth closed (silent)
                    character_sprite = closed_img
                
                # Overlay character at center
                if character_sprite is not None:
                    sprite_h, sprite_w = character_sprite.shape[:2]
                    x_offset = (width - sprite_w) // 2
                    y_offset = (height - sprite_h) // 2
                    img = overlay_image_with_alpha(img, character_sprite, x_offset, y_offset)
            else:
                # Fallback: Draw geometric shapes (original behavior)
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

                # Animated mouth - audio-reactive
                current_amplitude = amplitudes[i] if i < len(amplitudes) else 0.0
                mouth_base = 10
                mouth_variation = 15
                mouth_open = mouth_base + int(mouth_variation * current_amplitude)
                mouth_open = max(5, min(mouth_open, 25))  # Clamp between 5 and 25
                
                # Draw mouth ellipse
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
            
            # Draw Narrator Badge in the top-right corner
            if character_name:
                badge_text = "Narrator: Rachel Green"
                if character_name == "robot":
                    badge_text = "Narrator: Sheldon Cooper"
                elif character_name == "news_anchor":
                    badge_text = "Narrator: Michael Scott"
                
                # Draw badge background (semi-transparent dark gray box)
                badge_x1 = width - 280
                badge_y1 = 25
                badge_x2 = width - 25
                badge_y2 = 65
                
                overlay = img.copy()
                cv2.rectangle(overlay, (badge_x1, badge_y1), (badge_x2, badge_y2), (30, 30, 30), -1)
                cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
                
                # Draw border
                cv2.rectangle(img, (badge_x1, badge_y1), (badge_x2, badge_y2), (200, 180, 180), 1)
                # Draw text
                cv2.putText(img, badge_text, (badge_x1 + 15, badge_y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
            
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

@app.route('/')
def home():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/process', methods=['POST'])
def process():
    print("\n📨 RECEIVED REQUEST...")
    try:
        clean_old_files()
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        raw_text = data.get('content', '')
        url = data.get('url', '')
        character_name = data.get('character_name', 'girl')
        summary_length = data.get('summary_length', 'medium')
        
        # Determine number of sentences based on length
        if summary_length == 'short':
            script_count = 2
            notes_count = 2
        elif summary_length == 'long':
            script_count = 6
            notes_count = 6
        else: # medium
            script_count = 4
            notes_count = 4
        
        if not raw_text and url:
            print(f"🕸️ Scraping webpage content for landing page URL: {url}")
            raw_text = scrape_webpage_content(url)
            
        if not raw_text:
            return jsonify({"error": "No content could be extracted or provided. Check your input/URL."}), 400
        
        unique_id = str(int(time.time()))
        
        print("1️⃣ Generating Summary & Notes...")
        script = ""
        notes = []
        
        try:
            raw_summary = generate_smart_summary_and_notes(raw_text, character_name)
            if raw_summary and "---SCRIPT---" in raw_summary and "---NOTES---" in raw_summary:
                parts = raw_summary.split("---NOTES---")
                script = parts[0].replace("---SCRIPT---", "").strip()
                notes_text = parts[1].strip()
                notes = [line.strip().lstrip("-*•").strip() for line in notes_text.split("\n") if line.strip()]
            else:
                print("⚠️ Fallback: Could not parse structured notes, splitting by lines")
                if raw_summary:
                    script = raw_summary.replace("---SCRIPT---", "").replace("---NOTES---", "").strip()
                    sentences = [s.strip() for s in script.split('.') if s.strip()]
                    if len(sentences) > script_count:
                        script = ". ".join(sentences[:script_count]) + "."
                        notes = [s + "." for s in sentences[script_count:script_count+notes_count] if len(s) > 10]
                    else:
                        notes = ["Review the narration video for the full summary!"]
                else:
                    raise Exception("Empty Gemini response")
        except Exception as e:
            print(f"⚠️ Summary/Notes generation failed: {e}")
            # Heuristic fallback: clean text and extract sentences
            clean_text = raw_text.replace('\r', ' ').replace('\n', ' ').strip()
            sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 15]
            if len(sentences) >= script_count:
                base_script = ". ".join(sentences[:script_count]) + "."
                notes = [s + "." for s in sentences[script_count:script_count+notes_count] if len(s) > 20]
            else:
                base_script = raw_text[:300]
                notes = [
                    "Webpage content processed successfully.",
                    "Summary narration rendered using the chosen sitcom star.",
                    "Ready-made notes extracted directly from text."
                ]
            
            # Apply sitcom persona catchphrases to the script in Heuristic mode
            if character_name == "robot":
                script = (
                    "Greetings! According to physics and my own superior intellect, I have analyzed this webpage. "
                    f"Bazinga! Here is the precise summary: {base_script} "
                    "This summary is scientifically accurate, of course."
                )
            elif character_name == "news_anchor":
                script = (
                    "Alright, listen up, people! This is a big deal. Sometimes I start a sentence and I don't "
                    f"even know where it's going, but here is the summary: {base_script} "
                    "Yeah. That's what she said! Boom!"
                )
            else: # Rachel / girl
                script = (
                    "Oh my god! Okay, so I was reading this webpage, and I was like, I know, right? "
                    f"Here is what happened: {base_script} "
                    "Could this BE any more summarized? Seriously!"
                )
            
            # Ensure script has fallback
            if not script:
                script = raw_text[:300]
            # Ensure notes has fallback
            if not notes:
                notes = ["Review the narration video for the full summary!"]
            
        if not script:
            script = raw_text[:600]
            
        print(f"   ✅ Script generated ({len(script)} chars)")
        print(f"   ✅ Notes generated ({len(notes)} items)")
        
        print("2️⃣ Generating Audio (TTS)...")
        try:
            audio_filename = f"narration_{unique_id}.mp3"
            audio_path = os.path.join(STATIC_DIR, audio_filename)
            
            # Map sitcom characters to different Google TTS voice profiles (TLDs)
            if character_name == "robot":
                tld_val = "co.uk" # Sheldon - formal British accent
            elif character_name == "news_anchor":
                tld_val = "ca" # Michael - high-energy Canadian accent
            else:
                tld_val = "com" # Rachel - standard US accent
                
            tts = gTTS(script, lang='en', tld=tld_val)
            tts.save(audio_path)
            print(f"   ✅ Audio Saved ({character_name} voice profile)")
        except Exception as e:
            print(f"⚠️ Audio generation failed: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500
        
        print("3️⃣ Generating Video...")
        try:
            video_filename = f"video_{unique_id}.mp4"
            video_path = os.path.join(STATIC_DIR, video_filename)
            if character_name:
                print(f"   🎭 Character selected: {character_name}")
            success = create_avatar_video(script, audio_path, video_path, character_name=character_name)
            if not success:
                return jsonify({"error": "Video generation failed"}), 500
            print("   ✅ Video Saved")
        except Exception as e:
            print(f"⚠️ Video generation failed: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Video generation failed: {str(e)}"}), 500
 
        # Verify files exist before returning URLs
        video_exists = os.path.exists(video_path)
        audio_exists = os.path.exists(audio_path)
        
        if not video_exists:
            print(f"   ⚠️ Warning: Video file not found at {video_path}")
        if not audio_exists:
            print(f"   ⚠️ Warning: Audio file not found at {audio_path}")
        
        # Determine base URL dynamically based on the incoming request host
        base_url = request.host_url.rstrip('/')
        
        return jsonify({
            "status": "success",
            "script": script,
            "notes": notes,
            "video_url": f"{base_url}/static/{video_filename}" if video_exists else None,
            "audio_url": f"{base_url}/static/{audio_filename}" if audio_exists else None
        })
 
    except Exception as e:
        print("\n❌ CRITICAL SERVER CRASH ❌")
        print("--------------------------------------------------")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        traceback.print_exc()
        print("--------------------------------------------------")
        error_msg = str(e)
        if "character" in error_msg.lower() or "image" in error_msg.lower():
            error_msg = f"Character/image error: {error_msg}"
        elif "audio" in error_msg.lower():
            error_msg = f"Audio processing error: {error_msg}"
        return jsonify({"error": error_msg, "traceback": traceback.format_exc()}), 500

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
    print("Debug Server running on http://127.0.0.1:8080")
    app.run(port=8080, debug=False)