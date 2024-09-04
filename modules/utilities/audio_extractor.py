from moviepy.editor import VideoFileClip

def extract_audio_from_video(video_path, audio_output_path):
    """
    Extracts audio from video and saves result in WAV.
    """
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_output_path, codec='pcm_s16le')
    video.close()


