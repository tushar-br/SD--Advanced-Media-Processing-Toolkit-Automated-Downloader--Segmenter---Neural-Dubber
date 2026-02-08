from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import shutil
import yt_dlp
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from gtts import gTTS

# ============================================
# FLASK SERVER (AI PROCESSING ENGINE)
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMP_DIR = os.path.join(BASE_DIR, 'temp_processing') # Hidden Temp Folder

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# SAVE DIRECTLY TO DESKTOP (No Subfolder)
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')

# Ensure Temp Directory Exists
if os.path.exists(TEMP_DIR): shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR, exist_ok=True)

# -------------------------------------------------------------
# ROOT ROUTE
# -------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------------------------------------------
# API: VIDEO INFO
# -------------------------------------------------------------
@app.route('/api/video-info', methods=['POST'])
def video_info():
    try:
        url = request.json.get('url')
        if not url: return jsonify({'success': False, 'error': 'No URL'}), 400

        ydl_opts = {
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'quiet': False,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'socket_timeout': 30,
            # MIMIC ANDROID APP (Unblockable)
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if not info: return jsonify({'success': False, 'error': 'Failed to fetch info'}), 500

        # Formats
        formats = []
        if 'formats' in info:
            seen = set()
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':  # strict mp4
                    h = f.get('height')
                    if h and h not in seen:
                        # USE HEIGHT AS UNIQUE ID (e.g. 1080)
                        formats.append({
                            'format_id': str(h), 
                            'quality': f'{h}p', 
                            'mb': round(f.get('filesize',0)/1e6, 2) if f.get('filesize') else '?'
                        })
                        seen.add(h)
        # Sort High to Low
        formats.sort(key=lambda x: int(x['format_id']), reverse=True)

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

# -------------------------------------------------------------
# API: PROCESS & DOWNLOAD (THE BRAIN)
# -------------------------------------------------------------
@app.route('/api/process', methods=['POST'])
def process():
    try:
        data = request.json
        url = data.get('url')
        enable_dubber = data.get('enable_dubber', False)
        enable_segmenter = data.get('enable_segmenter', False)
        
        print(f"[INFO] Processing: {url} | Dub: {enable_dubber} | Seg: {enable_segmenter}")

        selected_fmt = data.get('format', 'best') # <--- FIXED MISSING VAR

        # 1. DETECT FFMPEG (From MoviePy)
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[INFO] Using FFmpeg at: {ffmpeg_path}")

        # 2. DOWNLOAD CHUNK
        ts = datetime.now().strftime("%H%M%S")
        temp_filename = f"temp_{ts}.mp4"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Determine Format (ROBUST MERGE)
        if selected_fmt and selected_fmt != 'best':
            # Get best video <= quality + best audio
            fmt_str = f'bestvideo[height<={selected_fmt}]+bestaudio/best[height<={selected_fmt}]/best'
        else:
            # Best everything
            fmt_str = 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': fmt_str,
            'outtmpl': temp_path,
            'ffmpeg_location': ffmpeg_path, # ImageIO FFmpeg
            'merge_output_format': 'mp4',   # <--- FORCE MERGE TO MP4 (Fixes Audio)
            'nocheckcertificate': True,
            'quiet': False,
            'socket_timeout': 30,
            'retries': 10,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')

        # 2. AI PROCESSING (MoviePy)
        processed_path = temp_path # Default
        final_suffix = ""

        if enable_dubber or enable_segmenter:
            try:
                clip = VideoFileClip(temp_path)
                
                # Apply Segmenter (First 30s)
                if enable_segmenter and clip.duration > 30:
                    clip = clip.subclip(0, 30)
                    final_suffix += "_Segmented"

                # Apply Neural Dub (AI Voice Overlay)
                if enable_dubber:
                    print("[INFO] Generating Neural Audio...")
                    uploader = info.get('uploader', 'Unknown Creator')
                    
                    # Clean text for TTS (Remove emojis/weird chars)
                    clean_text = "".join([c for c in video_title if c.isalnum() or c in " .,!?'"])
                    
                    # Smart Script
                    tts_text = f"Welcome. You are watching {clean_text}, created by {uploader}. This video has been processed using the Neural Dubbing Engine. The original audio has been replaced with this AI Voice. Enjoy the visual experience."
                    
                    tts_file = os.path.join(TEMP_DIR, "dub.mp3")
                    
                    # Generate Voice (Google Neural TTS)
                    tts = gTTS(text=tts_text, lang='en', tld='co.uk') # British Accent (More Professional)
                    tts.save(tts_file)
                    
                    # Merge & Loop Audio to fit video
                    dub_audio = AudioFileClip(tts_file)
                    
                    # If video is long, loop the speech or silence
                    if dub_audio.duration < clip.duration:
                        # Loop audio to fill time (or just play once at start)
                        final_audio = CompositeAudioClip([dub_audio.set_start(0)])
                    else:
                        final_audio = dub_audio.subclip(0, clip.duration)
                        
                    clip = clip.set_audio(final_audio)
                    final_suffix += "_AIDubbed"

                # Save Processed Version
                processed_filename = f"processed_{ts}.mp4"
                processed_path = os.path.join(TEMP_DIR, processed_filename)
                
                # Write File (Fastest Preset)
                clip.write_videofile(processed_path, codec='libx264', audio_codec='aac', preset='ultrafast', logger=None)
                
                # Close Clips
                clip.close()
                if enable_dubber: dub_audio.close()

            except Exception as e:
                print(f"[WARN] Processing Error: {e}")
                # Fallback to original if processing fails
                processed_path = temp_path

        # 3. MOVE TO DESKTOP (CLEAN NAME)
        clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ','-','_')]).rstrip()
        final_filename = f"{clean_title}{final_suffix}.mp4"
        final_dest = os.path.join(DESKTOP_PATH, final_filename)
        
        # Ensure unique name
        if os.path.exists(final_dest):
            final_filename = f"{clean_title}_{ts}{final_suffix}.mp4"
            final_dest = os.path.join(DESKTOP_PATH, final_filename)

        shutil.move(processed_path, final_dest)
        print(f"[SUCCESS] Saved to Desktop: {final_filename}")

        # 4. CLEANUP TEMP
        # Delete everything in temp folder to stay clean
        for f in os.listdir(TEMP_DIR):
            try:
                os.remove(os.path.join(TEMP_DIR, f))
            except: pass

        return jsonify({'success': True, 'files': [{'filename': final_filename}]})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # CLEAN START
    if os.path.exists(TEMP_DIR): shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
