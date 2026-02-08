"""
Media Segmenter Module
Splits video/audio into time-based segments
Uses MoviePy for video processing
"""

import os
from moviepy.editor import VideoFileClip, AudioFileClip
import logging

logger = logging.getLogger(__name__)


class MediaSegmenter:
    """Handles video and audio segmentation"""
    
    def __init__(self, download_folder):
        """
        Initialize segmenter
        
        Args:
            download_folder (str): Path to store segmented files
        """
        self.download_folder = download_folder
        self.segment_duration = 30  # Default: 30 seconds per segment
    
    def segment(self, filename, session_id, segment_duration=None):
        """
        Segment media file into multiple parts
        
        Args:
            filename (str): Input filename
            session_id (str): Unique session identifier
            segment_duration (int): Duration of each segment in seconds
            
        Returns:
            dict: Result with success status and list of segment filenames
        """
        try:
            if segment_duration:
                self.segment_duration = segment_duration
            
            input_path = os.path.join(self.download_folder, filename)
            
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': 'Input file not found'
                }
            
            logger.info(f"Starting segmentation for {filename}")
            
            # Determine if it's video or audio
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                return self._segment_video(input_path, session_id)
            elif file_ext in ['.mp3', '.wav', '.m4a', '.aac']:
                return self._segment_audio(input_path, session_id)
            else:
                # Try as video first
                return self._segment_video(input_path, session_id)
                
        except Exception as e:
            logger.error(f"Segmentation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _segment_video(self, input_path, session_id):
        """
        Segment video file
        
        Args:
            input_path (str): Path to input video
            session_id (str): Session identifier
            
        Returns:
            dict: Segmentation result
        """
        try:
            video = VideoFileClip(input_path)
            duration = video.duration
            
            logger.info(f"Video duration: {duration} seconds")
            
            # Calculate number of segments
            num_segments = int(duration / self.segment_duration) + 1
            
            # Limit to 5 segments for demo purposes
            num_segments = min(num_segments, 5)
            
            segment_files = []
            
            for i in range(num_segments):
                start_time = i * self.segment_duration
                end_time = min((i + 1) * self.segment_duration, duration)
                
                if start_time >= duration:
                    break
                
                # Create segment
                segment = video.subclip(start_time, end_time)
                
                # Generate output filename
                segment_filename = f'{session_id}_segment_{i+1}.mp4'
                segment_path = os.path.join(self.download_folder, segment_filename)
                
                # Write segment
                segment.write_videofile(
                    segment_path,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None  # Suppress MoviePy logs
                )
                
                segment_files.append(segment_filename)
                logger.info(f"Created segment {i+1}: {segment_filename}")
            
            # Close video
            video.close()
            
            return {
                'success': True,
                'segments': segment_files,
                'count': len(segment_files)
            }
            
        except Exception as e:
            logger.error(f"Video segmentation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _segment_audio(self, input_path, session_id):
        """
        Segment audio file
        
        Args:
            input_path (str): Path to input audio
            session_id (str): Session identifier
            
        Returns:
            dict: Segmentation result
        """
        try:
            audio = AudioFileClip(input_path)
            duration = audio.duration
            
            logger.info(f"Audio duration: {duration} seconds")
            
            # Calculate number of segments
            num_segments = int(duration / self.segment_duration) + 1
            
            # Limit to 5 segments for demo purposes
            num_segments = min(num_segments, 5)
            
            segment_files = []
            
            for i in range(num_segments):
                start_time = i * self.segment_duration
                end_time = min((i + 1) * self.segment_duration, duration)
                
                if start_time >= duration:
                    break
                
                # Create segment
                segment = audio.subclip(start_time, end_time)
                
                # Generate output filename
                segment_filename = f'{session_id}_segment_{i+1}.mp3'
                segment_path = os.path.join(self.download_folder, segment_filename)
                
                # Write segment
                segment.write_audiofile(
                    segment_path,
                    logger=None  # Suppress MoviePy logs
                )
                
                segment_files.append(segment_filename)
                logger.info(f"Created segment {i+1}: {segment_filename}")
            
            # Close audio
            audio.close()
            
            return {
                'success': True,
                'segments': segment_files,
                'count': len(segment_files)
            }
            
        except Exception as e:
            logger.error(f"Audio segmentation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
