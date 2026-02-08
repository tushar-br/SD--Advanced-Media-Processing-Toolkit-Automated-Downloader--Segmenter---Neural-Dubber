"""
Media Downloader Module
Downloads video/audio from URLs for educational purposes
Uses yt-dlp library for robust media downloading
"""

import os
import yt_dlp
import logging

logger = logging.getLogger(__name__)


class MediaDownloader:
    """Handles media downloading from various sources"""
    
    def __init__(self, download_folder):
        """
        Initialize downloader
        
        Args:
            download_folder (str): Path to store downloaded files
        """
        self.download_folder = download_folder
        os.makedirs(download_folder, exist_ok=True)
    
    def download(self, url, session_id):
        """
        Download media from URL
        
        Args:
            url (str): Media URL to download
            session_id (str): Unique session identifier
            
        Returns:
            dict: Result with success status and filename
        """
        try:
            logger.info(f"Starting download for session {session_id}")
            
            # Generate output filename
            output_template = os.path.join(
                self.download_folder,
                f'{session_id}_original.%(ext)s'
            )
            
            # Configure yt-dlp options with SSL fix
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Prefer MP4
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                # SSL certificate fix for educational use
                'nocheckcertificate': True,
                # Limit file size for educational demo (50MB)
                'max_filesize': 50 * 1024 * 1024,
                'progress_hooks': [self._progress_hook],
                # Additional options for better compatibility
                'ignoreerrors': False,
                'no_color': True,
                # Use legacy SSL for compatibility
                'legacy_server_connect': True,
            }
            
            # Download the media
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading from URL: {url}")
                info = ydl.extract_info(url, download=True)
                
                # Get the actual filename
                filename = ydl.prepare_filename(info)
                filename = os.path.basename(filename)
                
                logger.info(f"Download complete: {filename}")
                
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'ext': info.get('ext', 'mp4')
                }
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error: {str(e)}")
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _progress_hook(self, d):
        """
        Progress callback for download tracking
        
        Args:
            d (dict): Progress information from yt-dlp
        """
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            logger.info(f"Downloading: {percent} at {speed}")
        elif d['status'] == 'finished':
            logger.info("Download finished, processing...")
    
    def get_video_info(self, url):
        """
        Get video information without downloading
        
        Args:
            url (str): Media URL
            
        Returns:
            dict: Video information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', '')
                }
                
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
