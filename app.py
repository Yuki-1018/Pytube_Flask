from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # クロスドメイン通信を許可

def extract_video_info(entry):
    """
    個別の動画情報から音楽アプリで使いやすいようにフィールドを抽出・整形する
    """
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "audio_url": entry.get("url"),  # これが最高音質の直リンク
        "duration": entry.get("duration"),  # 秒数
        "thumbnail": entry.get("thumbnail"),
        "uploader": entry.get("uploader"),
        "channel": entry.get("channel"),
        "view_count": entry.get("view_count"),
        "upload_date": entry.get("upload_date"), # YYYYMMDD形式
        "description": entry.get("description"),
    }

@app.route('/api/extract', methods=['GET', 'POST'])
def extract_audio():
    # GETパラメーターまたはPOSTのJSONからURLを取得
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # yt-dlpのオプション設定
    ydl_opts = {
        # モバイル等で再生しやすいm4a形式の最高音質を優先、なければ他の最高音質
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': False,      # プレイリストのURLが来た場合、プレイリストとして処理する
        'extract_flat': False,    # 直リンクURLを解決するためFalseにする必要がある
        'quiet': True,            # コンソールへの不要な出力を抑える
        'skip_download': True,    # ダウンロードは行わない
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # URLから情報を抽出
            info = ydl.extract_info(url, download=False)
            
            # プレイリストか単一の動画かでレスポンスを分岐
            if 'entries' in info:
                # プレイリストの場合 (自動的に順番通りに取得されます)
                items = []
                for entry in info['entries']:
                    if entry:  # 削除された動画などでNoneになる場合があるためスキップ
                        items.append(extract_video_info(entry))
                
                response = {
                    "is_playlist": True,
                    "playlist_info": {
                        "id": info.get("id"),
                        "title": info.get("title"),
                        "uploader": info.get("uploader"),
                        "track_count": len(items)
                    },
                    "items": items
                }
            else:
                # 単一の動画の場合
                response = {
                    "is_playlist": False,
                    "playlist_info": None,
                    "items": [extract_video_info(info)]
                }
                
            return jsonify(response), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 開発用サーバー起動
    app.run(host='0.0.0.0', port=5000, debug=True)
