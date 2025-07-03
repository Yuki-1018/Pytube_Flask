from flask import Flask, render_template, request
from pytube import YouTube
import os

# Flaskアプリケーションの設定
app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def index():
    video_info = None
    error = None

    if request.method == "POST":
        video_url = request.form.get("url")

        try:
            # pytubefix を使ってBot検出回避（use_po_token=True）
            yt = YouTube(video_url, use_po_token=True)

            video_info = {
                "title": yt.title,
                "thumbnail_url": yt.thumbnail_url,
                "publish_date": yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else "不明",
                "video_streams": yt.streams.filter(adaptive=True, mime_type="video/mp4").order_by("resolution").desc(),
                "audio_streams": yt.streams.filter(only_audio=True).order_by("abr").desc(),
            }

        except Exception as e:
            error = f"エラー: {str(e)}"

    return render_template("index.html", video_info=video_info, error=error)

# Vercel が探すエクスポート名
handler = app
