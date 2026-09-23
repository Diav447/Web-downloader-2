from flask import Flask, request, render_template, jsonify, send_file, after_this_request
import yt_dlp
import os, uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "/tmp"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            heights = sorted(list(set([f.get('height') for f in info.get('formats', []) if f.get('height')])), reverse=True)
            formats_list = [{"quality": f"{h}p", "height": h} for h in heights if h >= 144]
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string'),
                "uploader": info.get('uploader'),
                "original_url": url,
                "formats": formats_list
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download')
def download_video():
    youtube_url = request.args.get('url')
    quality = request.args.get('q')
    uid = str(uuid.uuid4())
    out_template = os.path.join(DOWNLOAD_FOLDER, f"{uid}.%(ext)s")

    ydl_opts = {
        'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get('title', 'video')

        final_file = ""
        for f in os.listdir(DOWNLOAD_FOLDER):
            if uid in f:
                final_file = os.path.join(DOWNLOAD_FOLDER, f)
                break

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(final_file):
                    os.remove(final_file)
            except: pass
            return response

        return send_file(final_file, as_attachment=True, download_name=f"{title} - {quality}p.mp4")
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
