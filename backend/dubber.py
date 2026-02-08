"""
Neural Dubber Module (Demo Level)
Simulates AI-based voice dubbing for educational demonstration
Uses gTTS (Google Text-to-Speech) for voice synthesis
"""

import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)


class NeuralDubber:
    """Handles neural dubbing demonstration"""
    
    def __init__(self, download_folder):
        """
        Initialize neural dubber
        
        Args:
            download_folder (str): Path to store dubbed files
        """
        self.download_folder = download_folder
        self.temp_folder = os.path.join(download_folder, 'temp')
        os.makedirs(self.temp_folder, exist_ok=True)
    
    def dub(self, filename, session_id, text=None, language='en'):
        """
        Apply neural dubbing to media file (Demo)
        
        Args:
            filename (str): Input filename
            session_id (str): Unique session identifier
            text (str): Text for dubbing (optional)
            language (str): Language code for TTS
            
        Returns:
            dict: Result with success status and dubbed filename
        """
        try:
            input_path = os.path.join(self.download_folder, filename)
            
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': 'Input file not found'
                }
            
            logger.info(f"Starting neural dubbing for {filename}")
            
            # Default demo text if none provided
            if not text:
                text = (
                    "This is a demonstration of neural dubbing technology. "
                    "In a production system, this would use advanced AI models "
                    "to generate realistic voice dubbing. "
                    "This is an educational project for Software Development diploma."
                )
            
            # Determine if it's video or audio
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                return self._dub_video(input_path, session_id, text, language)
            elif file_ext in ['.mp3', '.wav', '.m4a', '.aac']:
                return self._dub_audio(input_path, session_id, text, language)
            else:
                # Try as video
                return self._dub_video(input_path, session_id, text, language)
                
        except Exception as e:
            logger.error(f"Dubbing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_voice(self, text, language, output_path):
        """
        Generate synthetic voice using TTS
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code
            output_path (str): Output audio file path
        """
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)
            logger.info(f"Generated voice audio: {output_path}")
            
        except Exception as e:
            logger.error(f"Voice generation error: {str(e)}")
            raise
    
    def _dub_video(self, input_path, session_id, text, language):
        """
        Dub video file with synthetic voice
        
        Args:
            input_path (str): Path to input video
            session_id (str): Session identifier
            text (str): Dubbing text
            language (str): Language code
            
        Returns:
            dict: Dubbing result
        """
        try:
            # Load video
            video = VideoFileClip(input_path)
            
            # Generate voice audio
            voice_audio_path = os.path.join(self.temp_folder, f'{session_id}_voice.mp3')
            self._generate_voice(text, language, voice_audio_path)
            
            # Load generated voice
            voice_audio = AudioFileClip(voice_audio_path)
            
            # Adjust voice duration to match video (loop or trim)
            if voice_audio.duration < video.duration:
                # Loop the voice audio
                loops_needed = int(video.duration / voice_audio.duration) + 1
                voice_audio = voice_audio.loop(n=loops_needed)
            
            # Trim to video duration
            voice_audio = voice_audio.subclip(0, min(voice_audio.duration, video.duration))
            
            # Replace video audio with dubbed voice
            dubbed_video = video.set_audio(voice_audio)
            
            # Generate output filename
            dubbed_filename = f'{session_id}_dubbed.mp4'
            dubbed_path = os.path.join(self.download_folder, dubbed_filename)
            
            # Write dubbed video
            dubbed_video.write_videofile(
                dubbed_path,
                codec='libx264',
                audio_codec='aac',
                logger=None
            )
            
            # Cleanup
            video.close()
            voice_audio.close()
            dubbed_video.close()
            
            # Remove temp voice file
            if os.path.exists(voice_audio_path):
                os.remove(voice_audio_path)
            
            logger.info(f"Created dubbed video: {dubbed_filename}")
            
            return {
                'success': True,
                'filename': dubbed_filename,
                'method': 'Neural TTS (Demo)'
            }
            
        except Exception as e:
            logger.error(f"Video dubbing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _dub_audio(self, input_path, session_id, text, language):
        """
        Replace audio file with synthetic voice
        
        Args:
            input_path (str): Path to input audio
            session_id (str): Session identifier
            text (str): Dubbing text
            language (str): Language code
            
        Returns:
            dict: Dubbing result
        """
        try:
            # Generate output filename
            dubbed_filename = f'{session_id}_dubbed.mp3'
            dubbed_path = os.path.join(self.download_folder, dubbed_filename)
            
            # Generate voice directly as output
            self._generate_voice(text, language, dubbed_path)
            
            logger.info(f"Created dubbed audio: {dubbed_filename}")
            
            return {
                'success': True,
                'filename': dubbed_filename,
                'method': 'Neural TTS (Demo)'
            }
            
        except Exception as e:
            logger.error(f"Audio dubbing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
