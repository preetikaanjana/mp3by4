import os
from dotenv import load_dotenv

# Load environment variables (tolerate non-UTF8 .env files)
try:
    load_dotenv()
except Exception:
    # Continue without .env if it cannot be decoded/parsed
    pass

# Configuration class
class Config:
    # Gemini API Key
    GEMINI_KEY = os.getenv('GEMINI_KEY', 'demo_key_for_testing')
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # File paths
    STATIC_FOLDER = 'static'
    OUTPUT_FOLDER = 'output'
    
    # Video settings
    DEFAULT_VIDEO_WIDTH = 640
    DEFAULT_VIDEO_HEIGHT = 480
    DEFAULT_FPS = 30
