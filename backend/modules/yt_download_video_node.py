from pytube import YouTube


def download_video_from_yt(vid_url: str):
    yt = YouTube(vid_url)
    t1 = yt.streams.filter(progressive=True, file_extension='mp4')
    t2 = t1.order_by('resolution')
    t3 = t2.desc()
    t4 = t3.first()
    t4.download()
    print("ALL GOOD!")

download_video_from_yt("https://www.youtube.com/watch?v=TPTrSrg3J4E")
