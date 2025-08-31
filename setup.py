#!/usr/bin/env python3
"""
Setup script for MP3by4 Chrome Extension
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("🐍 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r mp3by4/requirements.txt", "Installing requirements"):
        return False
    
    return True

def generate_extension_icons():
    """Generate extension icons"""
    print("🎨 Generating extension icons...")
    
    # Try to install cairosvg if not available
    try:
        import cairosvg
    except ImportError:
        print("📦 Installing cairosvg for icon generation...")
        if not run_command("pip install cairosvg", "Installing cairosvg"):
            print("⚠️  Icon generation failed, but extension will still work")
            return False
    
    # Generate icons
    if not run_command("cd extension && python generate_icons.py", "Generating icons"):
        print("⚠️  Icon generation failed, but extension will still work")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = "mp3by4/.env"
    if not os.path.exists(env_path):
        print("📝 Creating .env file...")
        env_content = """# Gemini API Key for AI text generation
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_KEY=your_gemini_api_key_here

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
        try:
            with open(env_path, 'w') as f:
                f.write(env_content)
            print("✅ .env file created")
            print("⚠️  Please edit mp3by4/.env and add your Gemini API key")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up MP3by4 Chrome Extension...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Generate extension icons
    generate_extension_icons()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit mp3by4/.env and add your Gemini API key")
    print("2. Run the Python server: cd mp3by4 && python server.py")
    print("3. Load the extension in Chrome: chrome://extensions/ -> Load unpacked -> select 'extension' folder")
    print("4. Navigate to any webpage and click the MP3by4 extension icon")
    print("\n💡 For help, check the README.md file")

if __name__ == "__main__":
    main()
