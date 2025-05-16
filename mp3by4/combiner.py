import subprocess

def combine_audio_video(video_path, audio_path, output_path):
    try:
        command = [
            'ffmpeg', '-y',  # Overwrite the output file
            '-i', video_path,  # Input video file
            '-i', audio_path,  # Input audio file
            '-c:v', 'copy',  # Copy video codec
            '-c:a', 'aac',  # Set audio codec
            '-strict', 'experimental',  # Allow experimental codecs
            output_path  # Output file
        ]
        subprocess.run(command)
        print(f"Video successfully saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

