from moviepy.editor import VideoFileClip, AudioFileClip

def replace_audio_in_video(in_audio_path: str, in_video_path: str, out_video_path: str, video_bitrate: str = '5000k'):
    video = VideoFileClip(in_video_path)
    audio = AudioFileClip(in_audio_path)

    video = video.set_audio(audio)

    video.write_videofile(out_video_path, codec='libx264', audio_codec='aac', bitrate=video_bitrate)

