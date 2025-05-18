@app.route('/generate', methods=['POST'])
def generate_video():
    data = request.get_json()
    quote = data.get('quote')
    image_url = data.get('imageUrl')
    music_url = data.get('musicUrl')

    if not all([quote, image_url, music_url]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Create paths
    import uuid
    import os
    OUTPUT_FOLDER = 'static/output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    image_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.jpg")
    music_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.mp3")
    video_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.mp4")

    # Download files
    import requests
    try:
        with open(image_path, 'wb') as f:
            f.write(requests.get(image_url).content)
        with open(music_path, 'wb') as f:
            f.write(requests.get(music_url).content)
    except Exception as e:
        return jsonify({'error': 'Failed to download media', 'detail': str(e)}), 500

   # Escape quote text safely
safe_quote = quote.replace("'", "\\'")

ffmpeg_command = [
    'ffmpeg',
    '-loop', '1',
    '-i', image_path,
    '-i', music_path,
    '-c:v', 'libx264',
    '-t', '10',
    '-vf', f"drawtext=text='{safe_quote}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
    '-pix_fmt', 'yuv420p',
    '-y',
    video_path
]


    # Run FFmpeg with error logging
    try:
        import subprocess
        print("📽️ Running FFmpeg Command:")
        print(" ".join(ffmpeg_command))
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ FFmpeg Success\n", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr captured"
        print("❌ FFmpeg error:", stderr_output)
        return jsonify({'error': 'FFmpeg processing failed', 'detail': stderr_output}), 500

    # Success response
    video_url = f"{request.host_url}static/output/{os.path.basename(video_path)}"
    return jsonify({'videoUrl': video_url})
