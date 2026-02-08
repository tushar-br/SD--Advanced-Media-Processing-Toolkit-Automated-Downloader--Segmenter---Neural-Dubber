from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import shutil
import yt_dlp
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from gtts import gTTS

# ============================================
# FLASK SERVER (HYBRID: LOCAL + VERCEL)
# ============================================

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# DETECT ENVIRONMENT
IS_VERCEL = os.environ.get('VERCEL') == '1'

# PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if IS_VERCEL:
    # Vercel: Use /tmp (Read/Write Allowed)
    TEMP_DIR = "/tmp/processing"
    DOWNLOAD_FOLDER = "/tmp/downloads"
else:
    # Local: Use Project Folder & Desktop
    TEMP_DIR = os.path.join(BASE_DIR, 'temp_processing')
    DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
    DOWNLOAD_FOLDER = os.path.join(DESKTOP_PATH, 'Media_Toolkit_Downloads')

# Init Folders
for d in [TEMP_DIR, DOWNLOAD_FOLDER]:
    if os.path.exists(d) and not IS_VERCEL: shutil.rmtree(d) # Clean start locally
    os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/video-info', methods=['POST'])
def video_info():
    try:
        url = request.json.get('url')
        if not url: return jsonify({'success': False, 'error': 'No URL'}), 400

        ydl_opts = {
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'quiet': True,
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if not info: return jsonify({'success': False, 'error': 'Failed to fetch info'}), 500

        formats = []
        if 'formats' in info:
            seen = set()
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    h = f.get('height')
                    if h and h not in seen:
                        formats.append({
                            'format_id': str(h), 
                            'quality': f'{h}p', 
                            'mb': round(f.get('filesize',0)/1e6, 2) if f.get('filesize') else '?'
                        })
                        seen.add(h)
        formats.sort(key=lambda x: int(x['format_id']) if x['format_id'].isdigit() else 0, reverse=True)

        return jsonify({
            'success': True,
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'views': info.get('view_count'),
            'formats': formats[:6]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process():
    try:
        data = request.json
        url = data.get('url')
        selected_fmt = data.get('format', 'best')
        enable_dubber = data.get('enable_dubber', False)
        enable_segmenter = data.get('enable_segmenter', False)
        
        # 1. SETUP FFMPEG
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        # 2. DOWNLOAD
        ts = datetime.now().strftime("%H%M%S")
        temp_filename = f"temp_{ts}.mp4"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        if selected_fmt and selected_fmt != 'best':
            fmt_str = f'bestvideo[height<={selected_fmt}]+bestaudio/best[height<={selected_fmt}]/best'
        else:
            fmt_str = 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': fmt_str,
            'outtmpl': temp_path,
            'ffmpeg_location': ffmpeg_path,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'quiet': False,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}, 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')

        # 3. PROCESSING (MoviePy)
        processed_path = temp_path
        final_suffix = ""

        if enable_dubber or enable_segmenter:
            try:
                clip = VideoFileClip(temp_path)
                if enable_segmenter and clip.duration > 30:
                    clip = clip.subclip(0, 30)
                    final_suffix += "_Segmented"

                if enable_dubber:
                    uploader = info.get('uploader', 'Unknown')
                    clean_text = "".join([c for c in video_title if c.isalnum() or c in " .,!?'"])
                    tts_text = f"Welcome. Watching {clean_text}, by {uploader}. Processed by Neural Dub Engine."
                    
                    tts_file = os.path.join(TEMP_DIR, "dub.mp3")
                    tts = gTTS(text=tts_text, lang='en', tld='co.uk')
                    tts.save(tts_file)
                    
                    dub_audio = AudioFileClip(tts_file)
                    if dub_audio.duration < clip.duration:
                        final_audio = CompositeAudioClip([dub_audio.set_start(0)])
                    else:
                        final_audio = dub_audio.subclip(0, clip.duration)
                    clip = clip.set_audio(final_audio)
                    final_suffix += "_AIDubbed"

                processed_filename = f"processed_{ts}.mp4"
                processed_path = os.path.join(TEMP_DIR, processed_filename)
                clip.write_videofile(processed_path, codec='libx264', audio_codec='aac', preset='ultrafast', logger=None)
                clip.close()
                if enable_dubber: dub_audio.close()
            except Exception as e:
                print(f"Processing Error: {e}")
                processed_path = temp_path

        # 4. FINALIZE (Local vs Vercel)
        clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ','-','_')]).rstrip()
        final_filename = f"{clean_title}{final_suffix}.mp4"
        
        if IS_VERCEL:
            # VERCEL: Move to accessible folder & Return URL
            vercel_dest = os.path.join(DOWNLOAD_FOLDER, final_filename)
            shutil.move(processed_path, vercel_dest)
            return jsonify({
                'success': True,
                'vercel': True,
                'download_url': f"/api/download_file?file={final_filename}", 
                'filename': final_filename
            })
        else:
            # LOCAL: Move to Desktop
            local_dest = os.path.join(DOWNLOAD_FOLDER, final_filename)
            if os.path.exists(local_dest): local_dest = os.path.join(DOWNLOAD_FOLDER, f"{clean_title}_{ts}{final_suffix}.mp4")
            shutil.move(processed_path, local_dest)
            
            # Cleanup Temp
            for f in os.listdir(TEMP_DIR):
                try: os.remove(os.path.join(TEMP_DIR, f))
                except: pass
                
            return jsonify({'success': True, 'vercel': False, 'files': [{'filename': os.path.basename(local_dest)}]})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download_file')
def download_file():
    fname = request.args.get('file')
    if not fname or '/' in fname: return "Invalid File", 400
    file_path = os.path.join(DOWNLOAD_FOLDER, fname)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
