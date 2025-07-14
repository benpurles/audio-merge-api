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

        # Check if we got HTML instead of audio (common with Google Drive)
        if 'text/html' in response.headers.get('Content-Type', ''):
            raise Exception("URL returned HTML instead of audio. Check the file's share settings or rehost it.")

        # Save streamed audio to a temp file to reduce memory usage
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            for chunk in response.iter_content(chunk_size=8192):
                temp_audio.write(chunk)
            temp_audio.flush()
            return AudioSegment.from_file(temp_audio.name, format="mp3")

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

        # Fetch both audio files
        audio1 = fetch_audio(url1)
        audio2 = fetch_audio(url2)

        # Merge audio files
        combined = audio1 + audio2

        # Export the result to a BytesIO buffer
        output_buffer = BytesIO()
        combined.export(output_buffer, format='mp3')
        output_buffer.seek(0)

        return send_file(
            output_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='merged_audio.mp3'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


