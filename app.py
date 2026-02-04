import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

def run_yt_dlp(url):
    """
    yt-dlpで音声メタデータ＋直リンク取得
    """
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-g",           # 直リンク
        "-J",           # JSONメタデータ
        "--flat-playlist",
        url
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout


@app.route("/audio", methods=["GET"])
def audio_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url parameter required"}), 400

    try:
        output = run_yt_dlp(url)
        lines = output.strip().splitlines()

        # -g はURLを先に吐く → 後半がJSON
        download_urls = []
        json_text = None

        for line in lines:
            if line.startswith("http"):
                download_urls.append(line)
            else:
                json_text = line

        data = json.loads(json_text)

        # 単体 or プレイリスト判定
        if "entries" in data:
            items = []
            for i, entry in enumerate(data["entries"]):
                items.append({
                    "index": i + 1,
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "duration": entry.get("duration"),
                    "uploader": entry.get("uploader"),
                    "webpage_url": entry.get("url"),
                    "download_url": download_urls[i] if i < len(download_urls) else None
                })
            return jsonify({
                "type": "playlist",
                "title": data.get("title"),
                "count": len(items),
                "items": items
            })

        else:
            return jsonify({
                "type": "single",
                "id": data.get("id"),
                "title": data.get("title"),
                "duration": data.get("duration"),
                "uploader": data.get("uploader"),
                "webpage_url": data.get("webpage_url"),
                "download_url": download_urls[0] if download_urls else None
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
