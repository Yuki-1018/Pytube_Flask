from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# CORS対策: 全てのオリジンからのアクセスを許可
CORS(app)

def extract_video_data(entry):
    """単一動画のデータを整形して返す"""
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "url": entry.get("url"),  # 音声または動画の直接リンク
        "duration": entry.get("duration"),
        "uploader": entry.get("uploader"),
        "thumbnail": entry.get("thumbnail"),
        "webpage_url": entry.get("webpage_url")
    }

@app.route('/api/extract', methods=['GET'])
def extract():
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({"error": "URL parameter is required"}), 400

    # yt-dlpの設定
        ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'noplaylist': False,
        # 以下の3行を追加（ボット検知回避の魔法の言葉）
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'po_token': ['web+web_embedded_player'],
            }
        }
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # メタデータの取得（ダウンロードはしない）
            info_dict = ydl.extract_info(target_url, download=False)
            
            results = []
            is_playlist = False
            playlist_title = None

            # プレイリストか単体かの判定
            if 'entries' in info_dict:
                is_playlist = True
                playlist_title = info_dict.get('title')
                # プレイリスト内の各動画を処理
                for entry in info_dict['entries']:
                    if entry: # entryがNoneでない場合のみ
                        results.append(extract_video_data(entry))
            else:
                # 単体動画
                results.append(extract_video_data(info_dict))

            return jsonify({
                "status": "success",
                "is_playlist": is_playlist,
                "playlist_title": playlist_title,
                "count": len(results),
                "data": results
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ローカルテスト用
if __name__ == '__main__':
    app.run(debug=True, port=5000)
