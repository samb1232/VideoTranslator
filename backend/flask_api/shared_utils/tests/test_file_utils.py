import unittest
from unittest.mock import patch, MagicMock
import os

from shared_utils import file_utils


class TestFileUtils(unittest.TestCase):
    def test_save_file(self):
        task_id = "01256129avbktiqhjcktqlctr45gFHFR413"
        extension = "txt"
        file = MagicMock()
        expected_filepath = os.path.join(file_utils.UPLOAD_FOLDER, task_id, f"{task_id}.{extension}")

        filepath = file_utils.save_file(file, extension, task_id)

        self.assertEqual(filepath, expected_filepath)


    def test_get_task_folder(self):
        task_id = "01256129avbktiqhjcktqlctr45gFHFR413"
        expected_folder_path = os.path.join(file_utils.UPLOAD_FOLDER, task_id)

        folder_path = file_utils.get_task_folder(task_id)

        self.assertEqual(folder_path, expected_folder_path)