from flask import Flask, render_template, request
from pytube import YouTube

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    video_info = None
    error = None

    if request.method == "POST":
        video_url = request.form.get("url")

        try:
            yt = YouTube(video_url)

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

if __name__ == "__main__":
    app.run(debug=True)
