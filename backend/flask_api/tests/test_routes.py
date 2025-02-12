from datetime import datetime
import json
import os
import shutil
import unittest
from unittest.mock import MagicMock, patch
from shared_utils.queue_tasks import VoiceGenQueueItem
from database.models import Task, User
from routes import create_blueprint
from flask import Flask
from flask_session import Session


class TestRoutes(unittest.TestCase):
    @patch('database.db_helper.DbHelper')
    @patch('rabbitmq_workers.RabbitMQConsumer')
    @patch('rabbitmq_workers.RabbitMQProducer')
    @patch('logging_conf.setup_logging')
    def setUp(self, mock_db_helper, mock_rmq_consumer, mock_rmq_producer, mock_logger):
        self.mock_db_helper = mock_db_helper.return_value
        self.mock_rmq_consumer = mock_rmq_consumer
        self.mock_rmq_producer = mock_rmq_producer
        self.app = Flask(__name__)
        self.app.config.from_mapping({
            "TESTING": True, 
            "SESSION_TYPE": "filesystem",
            "UPLOAD_FOLDER": 'test_uploads'
            })
        Session(self.app)
        bp = create_blueprint(self.mock_db_helper, self.mock_rmq_consumer, self.mock_rmq_producer)
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()
        
        self.upload_folder = self.app.config["UPLOAD_FOLDER"]
        os.makedirs(self.upload_folder)
        self.flask_session_folder = "flask_session"
        
        mock_logger.return_value = MagicMock()
        

    def tearDown(self):
        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)
        if os.path.exists(self.flask_session_folder):
            shutil.rmtree(self.flask_session_folder)
        
        
    def test_get_current_user_success(self):
        self.mock_db_helper.get_user_by_id.return_value = User(id="test_user_id", username="test_user", password="test_password")
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = "test_user_id"
        response = self.client.get("/@me")
        response_data = response.get_json()        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {
            'status': 'success',
            'id': "test_user_id",
            "username": "test_user",
            })


    def test_get_current_user_not_logged_in(self):
        self.mock_db_helper.get_user_by_id.return_value = None
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = None
        response = self.client.get("/@me")
        self.assertEqual(response.status_code, 401)
        
        
    def test_get_current_user_not_found(self):
        self.mock_db_helper.get_user_by_id.return_value = None
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = "test_user_id"
        response = self.client.get("/@me")
        self.assertEqual(response.status_code, 404)
        
    
    def test_login_user_success(self):
        test_user = User(id="test_user_id", username="test_user", password="test_password")
        self.mock_db_helper.get_user_by_username.return_value = test_user
        response = self.client.post("/login_user", json={
            'username': 'test_user',
            'password': 'test_password'
        })
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {
            'status': 'success',
            'id': 'test_user_id',
            'username': 'test_user'
        })     
      
    
    def test_login_user_user_not_found(self):
        self.mock_db_helper.get_user_by_username.return_value = None
        response = self.client.post("/login_user", json={
            'username': 'WRONG_USERNAME',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 401)
          
        
    def test_login_user_wrong_input(self):
        test_user = User(id="test_user_id", username="test_user", password="test_password")
        self.mock_db_helper.get_user_by_username.return_value = test_user
        response = self.client.post("/login_user", json={
            'username': 'test_user',
            'wrong field': 'and no password'
        })
        self.assertEqual(response.status_code, 400)
        
    
    def test_logout_user_success(self):
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = "test_user_id"
            
            response = self.client.post("/logout")   
            self.assertEqual(response.status_code, 200)
            
            with self.client.session_transaction() as session:
                self.assertNotIn("user_id", session)
        
    def test_logout_user_user_already_logged_out(self):
        with self.client:
            with self.client.session_transaction() as session:
                 session.pop("user_id", None)
            
            response = self.client.post("/logout")
            self.assertEqual(response.status_code, 404)
            
    
    def test_get_all_tasks_success(self):
        test_tasks = [
            Task(id="test_id_1",
                 number_id=1,
                 title="test_title_1",
                 creation_date=datetime(2025, 1, 1)
                 ),
            Task(id="test_id_2",
                 number_id=2,
                 title="test_title_2",
                 creation_date=datetime(2025, 1, 2)
                 ),
            Task(id="test_id_3",
                 number_id=3,
                 title="test_title_3",
                 creation_date=datetime(2025, 1, 3)
                 ),
            Task(id="test_id_4",
                 number_id=4,
                 title="test_title_4",
                 creation_date=datetime(2025, 1, 4)
                 ),
        ]
        test_tasks_json = []
        for task in test_tasks[::-1]:
            test_tasks_json.append(task.to_json())
            
        self.mock_db_helper.get_all_tasks_list.return_value = test_tasks
        
        with self.client:
            response = self.client.get("/get_all_tasks")
            self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertListEqual(response_data["tasks"], test_tasks_json)
    
    
    def test_get_all_tasks_wrong_order(self):
        test_tasks = [
            Task(id="test_id_1",
                 number_id=1,
                 title="test_title_1",
                 creation_date=datetime(2025, 1, 1)
                 ),
            Task(id="test_id_2",
                 number_id=2,
                 title="test_title_2",
                 creation_date=datetime(2025, 1, 2)
                 ),
            Task(id="test_id_3",
                 number_id=3,
                 title="test_title_3",
                 creation_date=datetime(2025, 1, 3)
                 ),
            Task(id="test_id_4",
                 number_id=4,
                 title="test_title_4",
                 creation_date=datetime(2025, 1, 4)
                 ),
        ]
        test_tasks_json = []
        for task in test_tasks[::-1]:
            test_tasks_json.append(task.to_json())  
        self.mock_db_helper.get_all_tasks_list.return_value = test_tasks
        test_tasks_wrong_order = [test_tasks_json[0], test_tasks_json[1], test_tasks_json[3], test_tasks_json[2]]
        response = self.client.get("/get_all_tasks")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertFalse(response_data["tasks"] == test_tasks_wrong_order)
    
    
    def test_get_task_success(self):
        test_task = Task(id="test_id_1", number_id=1, title="test_title_1")
        self.mock_db_helper.get_task_by_id.return_value = test_task
        response = self.client.get("/get_task/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {
            'status': 'success',
            'task_info': test_task.to_json()
        })

    def test_get_task_not_found(self):
        self.mock_db_helper.get_task_by_id.return_value = None
        response = self.client.get("/get_task/nonexistent_id")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data, {
            'status': 'error',
            'message': 'Task not found'
        })
    
    
    def test_create_task_success(self):
        test_task = Task(id="new_task_id", number_id=1, title="TEST_task_title")
        self.mock_db_helper.create_new_task.return_value = test_task
        response = self.client.post("/create_task", json={
            'title': 'TEST_task_title',
            'creator_username': 'test_user'
        })
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {
            'status': 'success',
            'task_id': 'new_task_id'
        })


    def test_create_task_missing_fields(self):
        response = self.client.post("/create_task", json={
            'title': 'TEST_task_title'
            # Missing 'creator_username'
        })
        self.assertEqual(response.status_code, 400)


    def test_delete_task_success(self):
        self.mock_db_helper.delete_task_by_id.return_value = True
        response = self.client.delete("/delete_task/existing_task_id")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {
            'status': 'success'
        })


    def test_delete_task_not_found(self):
        self.mock_db_helper.delete_task_by_id.return_value = False
        response = self.client.delete("/delete_task/nonexistent_task_id")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data, {
            'status': 'error',
            'message': 'Task not found'
        })
    
    
    # def test_download_file_success(self):
    #     test_file_path = os.path.join(self.upload_folder, "test_file.txt")
    #     with open(test_file_path, "w") as f:
    #         f.write("This is a test file.")

    #     response = self.client.get(f"/download/{test_file_path}")

    #     # Debugging: Print the response status code and content
    #     print(f"Response status code: {response.status_code}")
    #     print(f"Response data: {response.data.decode()}")

    #     # Assert the response status code and content
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.headers["Content-Disposition"], f"attachment; filename={os.path.basename(self.test_file_path)}")
    #     self.assertEqual(response.data.decode(), "This is a test file.")
    #     os.remove(test_file_path)
    
    
    def test_download_file_not_from_uploads(self):
        test_file_path = os.path.join("src", "test_file.txt")
        response = self.client.get(f"/download/{test_file_path}")
        self.assertEqual(response.status_code, 403)
        
        
    def test_get_json_subs_success(self):
        path_to_test_subs = os.path.join(self.upload_folder, "test_subs.json")
        with open(path_to_test_subs, "w", encoding='utf-8') as file:
            test_subs = [
                {
                    "end": "00:00:09,103",
                    "id": 1,
                    "modified": False,
                    "speaker": "A",
                    "start": "00:00:00,415",
                    "text": "TEST_SUBS_TEXT_1"
                },
                {
                    "end": "00:00:14,407",
                    "id": 2,
                    "modified": False,
                    "speaker": "A",
                    "start": "00:00:09,159",
                    "text": "TEST_SUBS_TEXT_2"
                }
            ]
            json.dump(test_subs, file, ensure_ascii=False, indent=4)
        test_task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path=path_to_test_subs)
        self.mock_db_helper.get_task_by_id.return_value = test_task
        response = self.client.get("/get_json_subs/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {'status': 'success', 'json_subs': test_subs})
        os.remove(path_to_test_subs)  
        
        
    def test_get_json_subs_task_not_found(self):
        self.mock_db_helper.get_task_by_id.return_value = None
        response = self.client.get("/get_json_subs/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 'error')
        

    def test_get_json_subs_no_subs_path(self):
        test_task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path="")
        self.mock_db_helper.get_task_by_id.return_value = test_task
        response = self.client.get("/get_json_subs/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 'error')
    
    
    def test_get_json_subs_file_not_found(self):
        path_to_test_subs = os.path.join(self.upload_folder, "test_subs.json")
        test_task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path=path_to_test_subs)
        self.mock_db_helper.get_task_by_id.return_value = test_task
        response = self.client.get("/get_json_subs/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 'error')
        
    
    def test_get_json_subs_wrong_json_format(self):
        path_to_test_subs = os.path.join(self.upload_folder, "test_subs.json")
        with open(path_to_test_subs, "w", encoding='utf-8') as file:
            test_wrong_subs = "SOME WRONG FORMAT"
            file.write(test_wrong_subs)
        test_task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path=path_to_test_subs)
        self.mock_db_helper.get_task_by_id.return_value = test_task
        response = self.client.get("/get_json_subs/test_id_1")
        response_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], 'error')
        os.remove(path_to_test_subs)  
        

    def test_save_subs_success(self):
        path_to_test_subs = os.path.join(self.upload_folder, "test_subs.json")
        task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path=path_to_test_subs)
        self.mock_db_helper.get_task_by_id.return_value = task
        valid_subs = [
            {
                "end": "00:00:09,103",
                "id": 1,
                "modified": False,
                "speaker": "A",
                "start": "00:00:00,415",
                "text": "TEST_SUBS_TEXT_1"
            }
        ]
        response = self.client.post("/save_subs/test_id_1", json={'json_subs': valid_subs})
        self.assertEqual(response.status_code, 202)
        self.assertTrue(os.path.exists(path_to_test_subs))
        with open(path_to_test_subs, "r") as f:
            response_subs = json.load(f)
        self.assertEqual(response_subs, valid_subs)
        os.remove(path_to_test_subs)
    
    def test_save_subs_no_subtitles_provided(self):
        response = self.client.post("/save_subs/test_id_1", json={})
        response_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], 'error')


    def test_save_subs_invalid_subtitles_format(self):
        invalid_subs = [{"invalid": "format"}]
        response = self.client.post("/save_subs/test_id_1", json={'json_subs': invalid_subs})
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'error')


    def test_save_subs_task_not_found(self):
        self.mock_db_helper.get_task_by_id.return_value = None
        valid_subs = [
            {
                "end": "00:00:09,103",
                "id": 1,
                "modified": False,
                "speaker": "A",
                "start": "00:00:00,415",
                "text": "TEST_SUBS_TEXT_1"
            }
        ]
        response = self.client.post("/save_subs/test_id_1", json={'json_subs': valid_subs})
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 'error')


    def test_save_subs_no_subs_path_for_task(self):
        task = Task(id="test_id_1", number_id=1, title="test_title_1", json_translated_subs_path=None)
        self.mock_db_helper.get_task_by_id.return_value = task
        valid_subs = [
            {
                "end": "00:00:09,103",
                "id": 1,
                "modified": False,
                "speaker": "A",
                "start": "00:00:00,415",
                "text": "TEST_SUBS_TEXT_1"
            }
        ]
        response = self.client.post("/save_subs/test_id_1", json={'json_subs': valid_subs})
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 'error')


    def test_generate_voice_success(self):
        src_audio_path_test = os.path.join(self.upload_folder, "src_audio.mp3")
        src_vid_path_test = os.path.join(self.upload_folder, "src_vid_.mp4")
        json_translated_subs_path_test = os.path.join(self.upload_folder, "json_translated.json")
        
        with open(src_audio_path_test, "wb") as file:
            file.write(b"audio file")
        with open(src_vid_path_test, "wb") as file:
            file.write(b"video file")
        with open(json_translated_subs_path_test, "w") as file:
            file.write("json subs")
        
        task = Task(
            id="test_id_1", 
            number_id=1, 
            title="test_title_1", 
            src_audio_path=src_audio_path_test, 
            src_vid_path=src_vid_path_test, 
            json_translated_subs_path=json_translated_subs_path_test,
            lang_to="en"
            )
        self.mock_db_helper.get_task_by_id.return_value = task
        response = self.client.post("/generate_voice/test_id_1")
        voice_task_item = VoiceGenQueueItem(
                task_id=task.id,
                src_audio_path=task.src_audio_path,
                src_video_path=task.src_vid_path,
                json_subs_path=task.json_translated_subs_path,
                lang_to=task.lang_to
                )
        self.assertEqual(response.status_code, 202)
        self.mock_rmq_producer.add_task_to_voice_gen_queue.assert_called_once_with(voice_task_item)


    def test_generate_voice_task_not_found(self):
        self.mock_db_helper.get_task_by_id.return_value = None
        response = self.client.post("/generate_voice/test_id_1")
        self.assertEqual(response.status_code, 404)
        self.mock_rmq_producer.add_task_to_voice_gen_queue.assert_not_called()
        
        
    def test_generate_voice_files_not_found(self):
        task = Task(
            id="test_id_1", 
            number_id=1, 
            title="test_title_1", 
            src_audio_path="NOT_EXISTNIG_PATH", 
            src_vid_path="NOT_EXISTNIG_PATH", 
            json_translated_subs_path="NOT_EXISTNIG_PATH",
            lang_to="en"
            )
        self.mock_db_helper.get_task_by_id.return_value = task
        response = self.client.post("/generate_voice/test_id_1")
        self.assertEqual(response.status_code, 404)
        self.mock_rmq_producer.add_task_to_voice_gen_queue.assert_not_called()

    