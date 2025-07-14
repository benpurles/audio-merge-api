from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return 'Audio Merge API is running!'

@app.route('/merge-audio', methods=['POST'])
def merge_audio():
    try:
        data = request.get_json()
        url1 = data.get('url1')
        url2 = data.get('url2')

        if not url1 or not url2:
            return jsonify({'error': 'Both url1 and url2 are required.'}), 400

        # Download and load audio files
        audio1 = AudioSegment.from_file(BytesIO(requests.get(url1).content))
        audio2 = AudioSegment.from_file(BytesIO(requests.get(url2).content))

        # Merge audio
        combined = audio1 + audio2

        # Export merged audio to buffer
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
