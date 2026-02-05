from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/extract', methods=['GET'])
def extract():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # 最小限の設定
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # プレイリスト・単体両方に対応
            info = ydl.extract_info(target_url, download=False)
            
            # infoがプレイリストの場合は 'entries' にリストが入る
            # 単体動画の場合は info 自体をリストに入れる
            entries = info.get('entries', [info])
            
            # 4項目に絞って整形
            results = []
            for e in entries:
                if e:
                    results.append({
                        "title": e.get("title"),
                        "uploader": e.get("uploader"),
                        "image": e.get("thumbnail"),
                        "audio_url": e.get("url")
                    })

            return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
