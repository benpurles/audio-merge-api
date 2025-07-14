from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import os
import requests
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/merge-audio', methods=['POST'])
def merge_audio():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON body provided'}), 400

        url1 = data.get('url1')
        url2 = data.get('url2')

        if not url1 or not url2:
            return jsonify({'error': 'Both url1 and url2 are required'}), 400

        def download_audio(url):
            r = requests.get(url)
            if r.status_code != 200:
                raise Exception(f"Failed to download from {url}")
            return BytesIO(r.content)

        audio1 = AudioSegment.from_file(download_audio(url1))
        audio2 = AudioSegment.from_file(download_audio(url2))
        combined = audio1 + audio2

        output = BytesIO()
        combined.export(output, format="mp3")
        output.seek(0)

        return send_file(output, mimetype='audio/mpeg', as_attachment=True, download_name='merged-audio.mp3')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



