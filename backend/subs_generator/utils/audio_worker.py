from moviepy.editor import VideoFileClip, AudioFileClip


def inject_audio_in_video(in_audio_path: str, in_video_path: str, out_video_path: str, video_bitrate: str = '5000k'):
    """
    Replaces audio in video and saves result in .mp4
    """
    video = VideoFileClip(in_video_path, audio=False)
    audio = AudioFileClip(in_audio_path)

    video = video.set_audio(audio)

    video.write_videofile(out_video_path, codec='libx264', audio_codec='aac', bitrate=video_bitrate)


def extract_audio_from_video(video_path: str, audio_output_path: str):
    """
    Extracts audio from video and saves result in WAV
    """
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_output_path)
    video.close()
