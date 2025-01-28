import unittest

from shared_utils import queue_tasks

class TestQueueTasks(unittest.TestCase):
    def test_subs_gen_queue_item_to_json(self):
        expected_str = """{
    "lang_from": "en",
    "lang_to": "ru",
    "task_id": "123123",
    "vid_filepath": "test_video.mp4"
}"""

        sg_item = queue_tasks.SubsGenQueueItem(
            task_id="123123",
            vid_filepath="test_video.mp4",
            lang_from="en",
            lang_to="ru"
        )
        self.assertEqual(sg_item.to_json(), expected_str)

    def test_subs_gen_queue_item_initialisation_from_json(self):
        input_str = """{
    "lang_from": "en",
    "lang_to": "ru",
    "task_id": "123123",
    "vid_filepath": "test_video.mp4"
}"""

        expected_item = queue_tasks.SubsGenQueueItem(
            task_id="123123",
            vid_filepath="test_video.mp4",
            lang_from="en",
            lang_to="ru"
        )

        item = queue_tasks.SubsGenQueueItem.from_json(input_str)

        self.assertEqual(item.task_id, expected_item.task_id)
        self.assertEqual(item.vid_filepath, expected_item.vid_filepath)
        self.assertEqual(item.lang_from, expected_item.lang_from)
        self.assertEqual(item.lang_to, expected_item.lang_to)

    def test_subs_gen_results_item_to_json(self):
        expected_str = """{
    "json_translated_subs_path": "test/translated_subs.json",
    "src_audio_path": "test/src_audio.mp3",
    "srt_orig_subs_path": "test/orig_subs.srt",
    "srt_translated_subs_path": "test/translated_subs.srt"
}"""

        sgr_item = queue_tasks.SubsGenResultsItem(
            src_audio_path = "test/src_audio.mp3",
            srt_orig_subs_path = "test/orig_subs.srt",
            srt_translated_subs_path = "test/translated_subs.srt",
            json_translated_subs_path = "test/translated_subs.json"
        )
        self.assertEqual(sgr_item.to_json(), expected_str)


    def test_subs_gen_result_item_initialisation_from_json(self):
        input_str = """{
    "json_translated_subs_path": "test/translated_subs.json",
    "src_audio_path": "test/src_audio.mp3",
    "srt_orig_subs_path": "test/orig_subs.srt",
    "srt_translated_subs_path": "test/translated_subs.srt"
}"""

        expected_item = queue_tasks.SubsGenResultsItem(
            src_audio_path = "test/src_audio.mp3",
            srt_orig_subs_path = "test/orig_subs.srt",
            srt_translated_subs_path = "test/translated_subs.srt",
            json_translated_subs_path = "test/translated_subs.json"
        )

        item = queue_tasks.SubsGenResultsItem.from_json(input_str)

        self.assertEqual(item.src_audio_path, expected_item.src_audio_path)
        self.assertEqual(item.srt_orig_subs_path, expected_item.srt_orig_subs_path)
        self.assertEqual(item.srt_translated_subs_path, expected_item.srt_translated_subs_path)
        self.assertEqual(item.json_translated_subs_path, expected_item.json_translated_subs_path)


    def test_voice_gen_queue_item_to_json(self):
        expected_str = """{
    "json_subs_path": "test/subs.json",
    "lang_to": "ru",
    "src_audio_path": "test/audio.mp3",
    "src_video_path": "test/video.mp4",
    "task_id": "123123"
}"""

        vg_item = queue_tasks.VoiceGenQueueItem(
            task_id = "123123",
            src_audio_path = "test/audio.mp3",
            src_video_path = "test/video.mp4",
            json_subs_path = "test/subs.json",
            lang_to = "ru"
        )
        self.assertEqual(vg_item.to_json(), expected_str)

    def test_voice_gen_queue_item_initialisation_from_json(self):
        input_str = """{
    "task_id": "123123",
    "src_audio_path": "test/audio.mp3",
    "src_video_path": "test/video.mp4",
    "json_subs_path": "test/subs.json",
    "lang_to": "ru"
}"""

        expected_item = queue_tasks.VoiceGenQueueItem(
            task_id = "123123",
            src_audio_path = "test/audio.mp3",
            src_video_path = "test/video.mp4",
            json_subs_path = "test/subs.json",
            lang_to = "ru"
        )

        item = queue_tasks.VoiceGenQueueItem.from_json(input_str)

        self.assertEqual(item.task_id, expected_item.task_id)
        self.assertEqual(item.src_audio_path, expected_item.src_audio_path)
        self.assertEqual(item.src_video_path, expected_item.src_video_path)
        self.assertEqual(item.json_subs_path, expected_item.json_subs_path)
        self.assertEqual(item.lang_to, expected_item.lang_to)

    def test_voice_gen_results_item_to_json(self):
        expected_str = """{
    "translated_audio_path": "test/translated_audio.mp3",
    "translated_video_path": "test/translated_video.mp4"
}"""

        vgr_item = queue_tasks.VoiceGenResultsItem(
            translated_audio_path = "test/translated_audio.mp3",
            translated_video_path = "test/translated_video.mp4",
        )
        self.assertEqual(vgr_item.to_json(), expected_str)


    def test_voice_gen_result_item_initialisation_from_json(self):
        input_str = """{
    "translated_audio_path": "test/translated_audio.mp3",
    "translated_video_path": "test/translated_video.mp4"
}"""

        expected_item = queue_tasks.VoiceGenResultsItem(
            translated_audio_path = "test/translated_audio.mp3",
            translated_video_path = "test/translated_video.mp4",
        )

        item = queue_tasks.VoiceGenResultsItem.from_json(input_str)

        self.assertEqual(item.translated_audio_path, expected_item.translated_audio_path)
        self.assertEqual(item.translated_video_path, expected_item.translated_video_path)






    def test_results_queue_item_to_json(self):
        expected_str = """{
    "op_status": "PROCESSING",
    "op_type": "SUBS_GEN",
    "task_id": "123123"
}"""

        res_item = queue_tasks.ResultsQueueItem(
            task_id = "123123",
            op_type = queue_tasks.RabbitMqOperationTypes.SUBS_GEN,
            op_status = queue_tasks.TaskStatus.PROCESSING,
            results = None
        )

        self.assertEqual(res_item.to_json(), expected_str)


    def test_results_queue_item_initialisation_from_json(self):
        input_str = """{
    "op_status": "PROCESSING",
    "op_type": "SUBS_GEN",
    "task_id": "123123"
}"""

        expected_item = queue_tasks.ResultsQueueItem(
            task_id = "123123",
            op_type = queue_tasks.RabbitMqOperationTypes.SUBS_GEN,
            op_status = queue_tasks.TaskStatus.PROCESSING,
            results = None
        )

        item = queue_tasks.ResultsQueueItem.from_json(input_str)

        self.assertEqual(item.op_status, expected_item.op_status)
        self.assertEqual(item.op_type, expected_item.op_type)
        self.assertEqual(item.task_id, expected_item.task_id)


    def test_items_from_wrong_json(self):
        wrong_json = """{
    "spam": "eggs",
    "hello": "world"
}"""
        with self.assertRaises(TypeError):
            queue_tasks.VoiceGenQueueItem.from_json(wrong_json)
        with self.assertRaises(TypeError):
            queue_tasks.VoiceGenResultsItem.from_json(wrong_json)
        with self.assertRaises(TypeError):
            queue_tasks.SubsGenQueueItem.from_json(wrong_json)
        with self.assertRaises(TypeError):
            queue_tasks.SubsGenResultsItem.from_json(wrong_json)
        with self.assertRaises(KeyError):
            queue_tasks.ResultsQueueItem.from_json(wrong_json)
