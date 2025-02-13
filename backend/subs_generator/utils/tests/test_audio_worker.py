import shutil
import unittest
import os
from moviepy.editor import VideoFileClip, AudioFileClip

from utils.audio_worker import extract_audio_from_video, inject_audio_in_video


class TestVideoAudioUtils(unittest.TestCase):
    def setUp(self):
        self.temp_folder = "temp_2"
        os.makedirs(self.temp_folder)
        self.test_video_path = os.path.joun(self.temp_folder, 'test_video.mp4')
        self.test_audio_path = os.path.joun(self.temp_folder, 'test_audio.wav')
        self.output_video_path = os.path.joun(self.temp_folder, 'output_video.mp4')
        self.output_audio_path = os.path.joun(self.temp_folder, 'output_audio.wav')

        VideoFileClip.create_black_video(self.test_video_path, duration=5)
        AudioFileClip.create_silent_audio(self.test_audio_path, duration=5)

    def tearDown(self):
        if os.path.exists(self.output_video_path):
            shutil.rmtree(self.temp_folder)

    def test_inject_audio_in_video(self):
        inject_audio_in_video(self.test_audio_path, self.test_video_path, self.output_video_path)

        self.assertTrue(os.path.exists(self.output_video_path))
        output_video = VideoFileClip(self.output_video_path)
        self.assertIsNotNone(output_video.audio)
        output_video.close()

    def test_extract_audio_from_video(self):
        extract_audio_from_video(self.test_video_path, self.output_audio_path)

        self.assertTrue(os.path.exists(self.output_audio_path))
        
        output_audio = AudioFileClip(self.output_audio_path)
        self.assertAlmostEqual(output_audio.duration, 5, delta=0.1)
        output_audio.close()
