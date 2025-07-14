 from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import requests
from io import BytesIO
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return 'Audio Merge API is running!'

def fetch_audio(url):
    try:
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()

        # Check for HTML content (e.g., failed link or preview page)
        if 'text/html' in response.headers.get('Content-Type', ''):
            raise Exception("URL returned HTML instead of audio. Check the link.")

        # Guess format from extension
        ext = url.split('.')[-1].split('?')[0].lower()
        audio_format = 'mp3' if ext not in ['m4a', 'aac', 'wav'] else ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_audio:
            for chunk in response.iter_content(chunk_size=8192):
                temp_audio.write(chunk)
            temp_audio.flush()
            return AudioSegment.from_file(temp_audio.name, format=audio_format)

    except Exception as e:
        raise Exception(f"Failed to fetch or decode audio from {url}: {e}")

@app.route('/merge-audio', methods=['POST'])
def merge_audio():
    try:
        data = request.get_json()
        url1 = data.get('url1')
        url2 = data.get('url2')

        if not url1 or not url2:
            return jsonify({'error': 'Both url1 and url2 are required.'}), 400

        audio1 = fetch_audio(url1)
        audio2 = fetch_audio(url2)
        combined = audio1 + audio2

        # Export to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
            combined.export(out_file.name, format='mp3')
            out_file.flush()

            # Upload to file.io
            with open(out_file.name, 'rb') as f:
                upload = requests.post("https://file.io", files={"file": f})
                if upload.status_code != 200:
                    raise Exception(f"Upload failed: {upload.text}")
                share_url = upload.json().get("link")

        return jsonify({'merged_url': share_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


