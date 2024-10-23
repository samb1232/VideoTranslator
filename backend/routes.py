import logging
from flask import jsonify, request, send_from_directory, session
from modules.utilities.sub_parser import check_json_subs_format
from modules.utilities.task_status_enum import TaskStatus
from database import db_operations
from database.models import Task, User
from modules.utilities.file_utils import save_file
import json
from workers import SubsCreatorQueueItem, VoiceGeneratorQueueItem, subs_queue, voice_queue

def register_routes(app):
    @app.route("/@me", methods=["GET"])
    def get_current_user():
        try:
            user_id = session["user_id"]
        except KeyError:
            user_id = None

        if not user_id:
            return jsonify({'status': 'error', "message": "User not logged in"}), 401

        user: User = db_operations.get_user_by_id(user_id)
        if user is None:
            return jsonify({'status': 'error', 'message': "User not found"}), 404
        return jsonify({
            'status': 'success',
            'id': user.id,
            "username": user.username,
            }), 200

    @app.route('/login_user', methods=['POST'])
    def login_user():
        request_json = request.json
        username = request_json['username']
        password = request_json['password']

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

        user: User = db_operations.get_user_by_username(username)

        if user is not None and user.password == password:
            session["user_id"] = user.id

            return jsonify({
                'status': 'success',
                "id":  user.id,
                "username": user.username
                }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

    @app.route("/logout", methods=["POST"])
    def logout_user():
        try:
            session.pop("user_id")
            return jsonify({'status': 'success'}), 200
        except KeyError:
            return jsonify({'status': 'error', "message": "User already logged out"}), 404

    @app.route("/get_all_tasks",  methods=["GET"])
    def get_all_tasks():
        tasks_arr = db_operations.get_all_tasks_list()
        tasks = []
        for task in tasks_arr:
            task_dict  = {
                "id": task.id,
                "title":  task.title,
                "last_used":  task.last_used
            }
            tasks.append(task_dict)
        # reverse tasks list and crop first 100 tasks
        tasks = tasks[::-1][:100]

        return jsonify({'status': 'success', "tasks":  tasks}), 200

    @app.route('/get_task/<id>', methods=['GET'])
    def get_task(id):
        task: Task = db_operations.get_task_by_id(id)
        if task is None:
            return jsonify({'status': 'error', "message":  "Task not found"}),  404
        return jsonify({'status': 'success', "task_info": task.to_json()}), 200

    @app.route("/create_task",  methods=["POST"])
    def create_task():
        title = request.json['title']
        logging.info(f"Creating new task: {title}")
        task = db_operations.create_new_task(title=title)
        return jsonify({'status': 'success', "task_id":  task.id}), 200

    @app.route('/delete_task/<id>', methods=['DELETE'])
    def delete_task(id):
        is_success = db_operations.delete_task_by_id(id)
        if is_success:
            return jsonify({'status': 'success'}), 200
        return jsonify({'status': 'error', "message": "Task not found"}),  404

    @app.route('/download/<path:filepath>')
    def download_file(filepath):
        if app.config["UPLOAD_FOLDER"] not in filepath:
            return jsonify({'status': 'error', "message":  f"Permission to download file {filepath} denied"}), 403
        return send_from_directory("./", filepath, as_attachment=True)

    @app.route('/get_video/<path:filepath>')
    def get_video(filepath):
        if app.config["UPLOAD_FOLDER"] not in filepath:
            return jsonify({'status': 'error', "message":  f"Permission to download file {filepath} denied"}), 403
        return send_from_directory("./", filepath)

    @app.route("/get_json_subs/<task_id>",  methods=["GET"])
    def get_json_subs(task_id):
        task = db_operations.get_task_by_id(task_id)
        if task is None:
            return jsonify({'status': 'error', "message":  "Task not found"}), 404
        subs_path = task.json_translated_subs_path
        if subs_path == "":
            return jsonify({'status': 'error', "message":  "No subs for this task"}), 404
        try:
            with open(subs_path, "r", encoding="utf-8") as json_file:
                json_subs = json.load(json_file)
        except FileNotFoundError:
            return jsonify({'status': 'error', 'message': 'Subtitles file not found'}), 404
        except json.JSONDecodeError:
            return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400

        return jsonify({'status': 'success', 'json_subs': json_subs}), 200
    
    @app.route("/save_subs/<task_id>", methods=["POST"])
    async def save_subs(task_id):
        try:
            new_subs = request.json.get('json_subs')
            if new_subs is None:
                return jsonify({'status': 'error', 'message': 'No subtitles provided'}), 400

            is_valid = check_json_subs_format(new_subs)

            if not is_valid:
                return jsonify({'status': 'error', 'message': 'Invalid subtitles format'}), 200

            task = db_operations.get_task_by_id(task_id)
            if task is None:
                return jsonify({'status': 'error', 'message': 'Task not found'}), 404

            subs_path = task.json_translated_subs_path
            if not subs_path:
                return jsonify({'status': 'error', 'message': 'No subs path for this task'}), 404

            with open(subs_path, "w") as json_file:
                json.dump(new_subs, json_file, indent=4)

        except Exception as e:
            err_message = str(e)
            logging.error(err_message)
            db_operations.set_task_voice_generation_status(task_id=task_id, status=TaskStatus.idle)
            return jsonify({'status': 'error', 'message': err_message}), 500

        return jsonify({'status': 'success'}), 202
    
    @app.route("/create_subs", methods=["POST"])
    async def create_subs():
        try:
            required_keys = {'task_id', 'lang_from', 'lang_to'}
            if not required_keys.issubset(request.values) or 'video_file' not in request.files:
                return jsonify({'status': 'error', 'message': 'Invalid request content'}), 400

            task_id = request.values["task_id"]
            video_file = request.files['video_file']
            lang_from = request.values["lang_from"]
            lang_to = request.values["lang_to"]

            if video_file.filename.split(".")[-1] != "mp4":
                return jsonify({'status': 'error', 'message': 'Invalid video file extension'}), 400
            
            vid_filepath = save_file(video_file, "mp4", task_id)

            subs_task_item = SubsCreatorQueueItem(
                task_id=task_id,
                vid_filepath=vid_filepath,
                lang_from=lang_from,
                lang_to=lang_to
            )
            subs_queue.put(subs_task_item)
            db_operations.set_task_subs_generation_status(task_id=task_id, status=TaskStatus.queued)

            return  jsonify({'status': 'success'}), 202
        except Exception as e:
            logging.error(str(e))
            db_operations.set_task_subs_generation_status(task_id=task_id, status=TaskStatus.idle)
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route("/generate_voice/<task_id>", methods=["POST"])
    def generate_voice(task_id):
        try:
            task = db_operations.get_task_by_id(task_id)
            if task is None:
                return jsonify({'status': 'error', 'message': 'Task not found'}), 404

            subs_path = task.json_translated_subs_path
            if not subs_path:
                return jsonify({'status': 'error', 'message': 'No subs path for this task'}), 404

            voice_task_item = VoiceGeneratorQueueItem(
                task_id=task_id,
                src_audio_path=task.src_audio_path,
                src_video_path=task.src_vid_path,
                json_subs_path=task.json_translated_subs_path,
                lang_to=task.lang_to
                )

            voice_queue.put(voice_task_item)
            db_operations.set_task_voice_generation_status(task_id=task_id, status=TaskStatus.queued)
        except Exception as e:
            err_message = str(e)
            logging.error(err_message)
            db_operations.set_task_voice_generation_status(task_id=task_id, status=TaskStatus.idle)
            return jsonify({'status': 'error', 'message': err_message}), 500

        return jsonify({'status': 'success'}), 202
