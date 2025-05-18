from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import uuid
import requests

app = Flask(__name__)
OUTPUT_FOLDER = 'static/output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate_video():
    data = request.get_json()
    quote = data.get('quote')
    image_url = data.get('imageUrl')
    music_url = data.get('musicUrl')

    if not all([quote, image_url, music_url]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Download image and music
    image_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.jpg")
    music_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.mp3")
    video_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.mp4")

    try:
        with open(image_path, 'wb') as f:
            f.write(requests.get(image_url).content)
        with open(music_path, 'wb') as f:
            f.write(requests.get(music_url).content)
    except Exception as e:
        return jsonify({'error': 'Failed to download media'}), 500

    # Create video using FFmpeg
    ffmpeg_command = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', music_path,
        '-c:v', 'libx264',
        '-t', '10',
        '-vf', f"drawtext=text='{quote}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
        '-pix_fmt', 'yuv420p',
        '-y',
        video_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'FFmpeg processing failed'}), 500

    video_url = f"{request.host_url}static/output/{os.path.basename(video_path)}"
    return jsonify({'videoUrl': video_url})

if __name__ == '__main__':
    app.run(debug=True)
