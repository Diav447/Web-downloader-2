from flask import Flask, request, jsonify, render_template_string
import yt_dlp
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YTLite - Fix Audio</title>
<style>
body{background:#0a0a0a;color:white;font-family:sans-serif;padding:20px}
input{width:70%;padding:12px;border-radius:12px;border:none;background:#222;color:white}
button{padding:12px 20px;border-radius:12px;border:none;background:#8b5cf6;color:white;font-weight:bold;cursor:pointer}
.card{background:#18181b;padding:15px;border-radius:12px;margin-top:15px}
a{color:#a78bfa}
</style>
</head>
<body>
<h1>YTLite.</h1>
<p>Semua kualitas ada suara 🔊 no tipu-tipu</p>
<input id="url" placeholder="https://youtube.com/watch?v=...">
<button onclick="gas()">GAS</button>
<div id="result"></div>
<script>
async function gas(){
  let url=document.getElementById('url').value;
  if(!url)return alert('link mana wee?');
  document.getElementById('result').innerHTML='Lagi ngeracik video + audio... ⏳';
  let res=await fetch('/download?url='+encodeURIComponent(url));
  let data=await res.json();
  if(data.error){
    alert('ERROR: '+data.error);
    document.getElementById('result').innerHTML='';
    return;
  }
  let h='';
  data.formats.forEach(f=>{
    h+=`<div class="card"><b>${f.height ? f.height+'p' : 'Audio'} - ${f.ext}</b> (${f.filesize || 'auto'})<br><a href="${f.url}" target="_blank" download>Download</a></div>`;
  });
  document.getElementById('result').innerHTML=h;
}
</script>
</body>
</html>
"""

# INI OBAT ANTI BOT YOUTUBE 2026
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios', 'web'],
            'player_skip': ['webpage', 'configs'],
        }
    },
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
}

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url kosong wee'}), 400
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', [])[-15:]: # ambil 15 terakhir biar gak kebanyakan
                if f.get('url'):
                    formats.append({
                        'url': f['url'],
                        'ext': f.get('ext'),
                        'height': f.get('height'),
                        'filesize': f.get('filesize_human') or f.get('filesize'),
                    })
            # reverse biar 1080p di atas
            formats = list(reversed(formats))
            return jsonify({'title': info.get('title'), 'formats': formats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Buat Vercel
if __name__ == '__main__':
    app.run()
