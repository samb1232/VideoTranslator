from datetime import datetime
import os
from flask import Flask, jsonify, request, send_file, send_from_directory, session
from flask_cors import CORS
from flask_session import Session
from database import db_operations
from modules.subs_generator import SubsGenerator
from modules.subs_translator import SubsTranslator, Translators
from modules.utilities.file_utils import get_task_folder, save_file
from config import ConfigWeb
from database.models import Task, User, db

app = Flask(__name__)
app.config.from_object(ConfigWeb)
CORS(app, supports_credentials=True)

server_session = Session(app)

db.init_app(app)
with app.app_context():
    db.create_all()
    db_operations.reset_all_task_processing()

@app.route("/@me", methods=["GET"])  
def get_current_user():
    try:
        user_id = session["user_id"]
    except KeyError as e:
        user_id = None
        
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    user: User = db_operations.get_user_by_id(user_id)
    return jsonify({
            'id': user.id,
            "username": user.username,
            })


@app.route('/login', methods=['POST'])
def login_user():
    request_json = request.json
    username = request_json['username']
    password = request_json['password']

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    user: User = db_operations.get_user_by_username(username)

    if user is not None and user.password == password:
        session["user_id"] = user.id

        return jsonify({
            "id":  user.id,
            "username": user.username
            })

    else:
        return jsonify({'message': 'Invalid username or password'}), 401 


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"


@app.route("/create_subs", methods=["POST"])
def create_subs():
    try:
        required_keys = {'task_id', 'lang_from', 'lang_to'}
        if not required_keys.issubset(request.values) or 'video_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'Invalid request content'}), 400

        video_file = request.files['video_file']
        task_id = request.values["task_id"]
        lang_from = request.values["lang_from"]
        lang_to = request.values["lang_to"]

        db_operations.set_task_subs_generation_processing(task_id=task_id, value=True)

        if video_file.filename.split(".")[-1] != "mp4":
            return jsonify({'status': 'error', 'message': 'Invalid video file extension'}), 400
        vid_filepath = save_file(video_file, "mp4", task_id)
        
        task_folder = get_task_folder(task_id)

        subs_generator = SubsGenerator(
            src_lang=lang_from,
        )
        subs_generator.transcript(
            video_file_path=vid_filepath,
            output_dir=task_folder
        )
        
        json_filepath = subs_generator.get_json_out_filepath()
        srt_filepath = subs_generator.get_srt_out_filepath()
        audio_filepath = subs_generator.get_audio_out_filepath()

        print("Subtitles trancribed!")

        subs_translator = SubsTranslator(
            translator=Translators.yandex,
            source_lang=lang_from,
            target_lang=lang_to
            )
        srt_tranlsated_filepath = os.path.join(task_folder, f"{task_id}_translated.srt")
        json_tranlsated_filepath = os.path.join(task_folder, f"{task_id}_translated.json")

        subs_translator.translate_srt_file(srt_filepath, srt_tranlsated_filepath)
        subs_translator.translate_json_file(json_filepath, json_tranlsated_filepath)

        db_operations.update_task_after_subs_created(
            task_id=task_id,
            lang_from=lang_from,
            lang_to=lang_to,
            src_vid_path=vid_filepath,
            src_audio_path=audio_filepath,
            srt_orig_subs_path=srt_filepath,
            srt_translated_subs_path=srt_tranlsated_filepath,
            json_translated_subs_path=json_tranlsated_filepath
        )
        return  jsonify({'status': 'success'}), 200
    except Exception as e:
        print(e)
        db_operations.set_task_subs_generation_processing(task_id=task_id, value=False)
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route("/get_all_tasks",  methods=["GET"])
def  get_all_tasks():
    tasks_arr = db_operations.get_all_tasks_list()
    tasks = []
    for task in tasks_arr:
        task_dict  = {
            "id": task.id,
            "title":  task.title,
            "last_used":  task.last_used
        }
        tasks.append(task_dict)
    # reverse tasks list
    tasks.reverse()
    return jsonify({'status': 'success', "tasks":  tasks}), 200


@app.route('/get_task/<id>', methods=['GET'])
def get_task(id):
    task: Task = db_operations.get_task_by_id(id)
    if task is None:
        return jsonify({'status': 'error', "message":  "Task not found"}),  404
    
    return jsonify({'status': 'success', "task_info": task.to_json()}), 200


@app.route("/create_task",  methods=["POST"])
def  create_task():
    request_json = request.json
    title = request_json['title']
    task = db_operations.create_new_task(title=title)
    return jsonify({'status': 'success', "task_id":  task.id}), 200


@app.route('/delete_task/<id>', methods=['DELETE'])
def delete_task(id):
    is_success = db_operations.delete_task_by_id(id)
    if is_success:
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', "message":  "Task not found"}),  404
    

@app.route('/download/<path:filepath>')
def download_file(filepath):
    if app.config["UPLOAD_FOLDER"] not in filepath:
        return jsonify({'status': 'error', "message":  f"Permission to download file {filepath} denided"}), 403
    return send_from_directory("../", filepath, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=False)
