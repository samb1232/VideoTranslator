from datetime import datetime
import json
import unittest
import os
from unittest.mock import patch, MagicMock
from database.models import Task, User
from database.db_helper import DbHelper
import shutil


class TestDatabaseHelper(unittest.TestCase):
    TEMP_DIR = "temp"

    @patch('database.db_helper.create_engine')
    @patch('database.db_helper.sessionmaker')
    def setUp(self, mock_sessionmaker, mock_create_engine):
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        
        self.mock_engine = MagicMock()
        mock_create_engine.return_value = self.mock_engine

        self.mock_session_factory = MagicMock()
        mock_sessionmaker.return_value = self.mock_session_factory
        
        self.mock_session = MagicMock()
        self.mock_session_factory.return_value = self.mock_session
        
        self.db_helper = DbHelper()
        self.db_helper.Session = self.mock_session_factory
        self.db_helper.engine = self.mock_engine

    def tearDown(self):
        if os.path.exists(self.TEMP_DIR):
            shutil.rmtree(self.TEMP_DIR)


    def test_add_users_success(self):
        users_data = [
            {"username": "testuser1", "password": "password1"},
            {"username": "testuser2", "password": "password2"}
        ]

        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = None
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        self.db_helper.add_users(users_data)

        self.mock_session.query.assert_called()
        self.mock_session.add.assert_called() 
        self.mock_session.commit.assert_called_once()
        self.mock_session.rollback.assert_not_called()
        self.mock_session.close.assert_called_once()


    def test_add_users_already_exists(self):
        users_data = [
            {"username": "testuser1", "password": "password1"}
        ]

        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = User(username = "testuser1", password="password1")
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        self.db_helper.add_users(users_data)

        self.mock_session.query.assert_called()
        self.mock_session.add.assert_not_called() 
        self.mock_session.commit.assert_called_once()
        self.mock_session.rollback.assert_not_called()
        self.mock_session.close.assert_called_once()


    def test_add_users_key_error(self):
        users_data = [
            {"username": "testuser1"}, # Missing password
        ]

        self.db_helper.add_users(users_data)

        self.mock_session.query.assert_not_called()
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
    
    def test_check_users_format_raises_error(self):
        users_data = [
            {"username": "testuser1", "password": "password1"},
            {"username": "testuser2"} # Missing password
        ]
        with self.assertRaises(KeyError):
            self.db_helper.check_users_format(users_data)
            
    def test_check_users_format_passes(self):
        users_data = [
            {"username": "testuser1", "password": "password1"},
            {"username": "testuser2", "password": "password2"},
            {"username": "testuser3", "password": "password3"},
            {"username": "testuser4", "password": "password4"},
            {"username": "testuser5", "password": "password5"},
        ]
        self.db_helper.check_users_format(users_data)
    
    @patch("database.db_helper.DbHelper.add_users")
    def test_add_users_from_json(self, mock_add_users):
        users_data = [
            {"username": "testuser1", "password": "password1"},
            {"username": "testuser2", "password": "password2"},
            {"username": "testuser3", "password": "password3"},
            {"username": "testuser4", "password": "password4"},
            {"username": "testuser5", "password": "password5"},
        ]
        json_path = os.path.join(self.TEMP_DIR, "test_users.json")
        with open(json_path, "w") as f:
            json.dump(users_data, f)
        
        self.db_helper.add_users_from_json(json_path)
    
        mock_add_users.assert_called_once_with(users_data)
        
    
    def test_get_user_by_username_existing_user(self):
        username = "testuser1"
        password="password1"
        mock_user = MagicMock(spec=User, username=username, password=password)
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_user
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        user = self.db_helper.get_user_by_username(username)

        self.mock_session.query.assert_called_with(User)
        mock_query.filter_by.assert_called_with(username=username)
        mock_filter_by.first.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertEqual(user, mock_user) 
        
        
    def test_get_user_by_username_none(self):
        username = "testuser1"
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = None
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        user = self.db_helper.get_user_by_username(username)

        self.mock_session.query.assert_called_with(User)
        mock_query.filter_by.assert_called_with(username=username)
        mock_filter_by.first.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertIsNone(user) 
    
      
    
    def test_get_user_by_id_existing_user(self):
        id = "lkegjposdjgeoi123"
        mock_user = MagicMock(spec=User, id=id, username="username1", password="password1")
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_user
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        user = self.db_helper.get_user_by_id(id)

        self.mock_session.query.assert_called_with(User)
        mock_query.filter_by.assert_called_with(id=id)
        mock_filter_by.first.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertEqual(user, mock_user) 
        
        
    def test_get_user_by_id_none(self):
        id = "NOT_EXISTING_ID"
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = None
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query

        user = self.db_helper.get_user_by_id(id)

        self.mock_session.query.assert_called_with(User)
        mock_query.filter_by.assert_called_with(id=id)
        mock_filter_by.first.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertIsNone(user) 
        
    def test_create_new_task(self):
        new_task_title = "test_title"
        creator_username = "testuser"
        new_task = Task(
            title=new_task_title,
            creator_username=creator_username,
            last_used=datetime.now(),
            creation_date=datetime.now()
        )
        
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        result = self.db_helper.create_new_task(new_task_title, creator_username)
        
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertEqual(result.title, new_task.title)
        self.assertEqual(result.creator_username, new_task.creator_username)
        
    
    def test_get_task_by_id(self):
        test_id = "h2wt23tbvdfbAFgw2"
        mock_task = MagicMock(spec=Task, id=test_id, title="test", creator_username="test_user")
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_task
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query
        
        task = self.db_helper.get_task_by_id(test_id)
        
        self.mock_session.query.assert_called_with(Task)
        mock_query.filter_by.assert_called_with(id=test_id)
        mock_filter_by.first.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.assertEqual(task, mock_task)
        
    def test_delete_task_by_id_success(self):
        test_id = "h2wt23tbvdfbAFgw2"
        mock_task = MagicMock(spec=Task, id=test_id, title="test", creator_username="test_user")
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_task
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query
        
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        is_sucess = self.db_helper.delete_task_by_id(test_id)
        
        self.mock_session.query.assert_called_with(Task)
        mock_query.filter_by.assert_called_with(id=test_id)
        mock_filter_by.first.assert_called_once()
        self.mock_session.delete.assert_called_once_with(mock_task)
        self.mock_session.close.assert_called_once()
        self.assertTrue(is_sucess)
        
        
    def test_delete_task_by_id_task_not_found(self):
        test_id = "NOT_EXISTING_ID"
        
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = None
        mock_query.filter_by.return_value = mock_filter_by
        self.mock_session.query.return_value = mock_query
        
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        is_sucess = self.db_helper.delete_task_by_id(test_id)
        
        self.mock_session.query.assert_called_with(Task)
        mock_query.filter_by.assert_called_with(id=test_id)
        mock_filter_by.first.assert_called_once()
        self.mock_session.delete.assert_not_called()
        self.mock_session.close.assert_called_once()
        self.assertFalse(is_sucess)
        
