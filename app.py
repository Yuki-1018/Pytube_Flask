from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) # CORS対策

def format_entry(entry):
    """必要な4項目だけに絞り込む"""
    return {
        "title": entry.get("title"),
        "uploader": entry.get("uploader"),
        "image": entry.get("thumbnail"),
        "audio_url": entry.get("url") # 直リンク
    }

@app.route('/api/extract', methods=['GET'])
def extract():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        # プレイリストが巨大な場合のタイムアウト対策
        'playlist_items': '1-20', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            
            # プレイリストか単体かを判定してリスト化
            entries = info.get('entries', [info])
            
            # Noneを除去しつつ整形
            results = [format_entry(e) for e in entries if e]

            return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel用
app.debug = False
