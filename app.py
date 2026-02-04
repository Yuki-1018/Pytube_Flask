import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

def yt_json(url):
    cmd = ["yt-dlp", "-J", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)

def yt_audio_url(url):
    cmd = ["yt-dlp", "-f", "bestaudio", "-g", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.strip().splitlines()[0]

@app.route("/audio")
def audio():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url required"}), 400

    try:
        data = yt_json(url)

        # プレイリスト
        if "entries" in data:
            items = []
            for entry in data["entries"][:10]:  # 🔴 Vercel対策：最大10件
                video_url = entry.get("webpage_url")
                if not video_url:
                    continue

                audio_url = yt_audio_url(video_url)

                items.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "duration": entry.get("duration"),
                    "download_url": audio_url
                })

            return jsonify({
                "type": "playlist",
                "title": data.get("title"),
                "count": len(items),
                "items": items
            })

        # 単体動画
        audio_url = yt_audio_url(url)
        return jsonify({
            "type": "single",
            "id": data.get("id"),
            "title": data.get("title"),
            "duration": data.get("duration"),
            "download_url": audio_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
