import json
import threading
from flask import Blueprint, jsonify, request, send_from_directory, session, current_app
from database.db_helper import DbHelper
from logging_conf import setup_logging
from rabbitmq_workers import RabbitMQConsumer, RabbitMQProducer
from shared_utils.queue_tasks import SubsGenQueueItem, VoiceGenQueueItem
from shared_utils.sub_parser import validate_json_subs_format, convert_subtitles_to_json_arr, parse_json_to_subtitles
from shared_utils.file_utils import save_file


logger = setup_logging()

db_operations: DbHelper = DbHelper()

bp = Blueprint('routes', __name__)
rabbitmq_client = RabbitMQProducer()

rabbitmq_res_consumer = RabbitMQConsumer()

threading.Thread(target=rabbitmq_res_consumer.watch_results_queue, daemon=True).start()
   
    
@bp.route("/@me", methods=["GET"])
def get_current_user():
    try:
        user_id = session["user_id"]
    except KeyError:
        user_id = None
    if not user_id:
        return jsonify({'status': 'error', "message": "User not logged in"}), 401
    
    user = db_operations.get_user_by_id(user_id)
    if user is None:
        return jsonify({'status': 'error', 'message': "User not found"}), 404
    return jsonify({
        'status': 'success',
        'id': user.id,
        "username": user.username,
        }), 200


@bp.route('/login_user', methods=['POST'])
def login_user():
    request_json = request.json
    username = request_json['username']
    password = request_json['password']

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

    user = db_operations.get_user_by_username(username)

    if user is not None and user.password == password:
        session["user_id"] = user.id
        
        return jsonify({
            'status': 'success',
            "id":  user.id,
            "username": user.username
            }), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401


@bp.route("/logout", methods=["POST"])
def logout_user():
    try:
        session.pop("user_id")
        return jsonify({'status': 'success'}), 200
    except KeyError:
        return jsonify({'status': 'error', "message": "User already logged out"}), 404


@bp.route("/get_all_tasks",  methods=["GET"])
def get_all_tasks():
    tasks_arr = db_operations.get_all_tasks_list()
    tasks = []
    for task in tasks_arr:
        tasks.append(task.to_json())
    # reverse tasks list and crop first 100 tasks
    tasks = tasks[::-1][:100]
    return jsonify({'status': 'success', "tasks":  tasks}), 200


@bp.route('/get_task/<id>', methods=['GET'])
def get_task(id):
    task = db_operations.get_task_by_id(id)
    if task is None:
        return jsonify({'status': 'error', "message":  "Task not found"}),  404
    return jsonify({'status': 'success', "task_info": task.to_json()}), 200


@bp.route("/create_task",  methods=["POST"])
def create_task():
    title = request.json['title']
    creator_username = request.json['creator_username']
    logger.info(f"Creating new task: {title}")
    task = db_operations.create_new_task(title=title, creator_username=creator_username)
    return jsonify({'status': 'success', "task_id":  task.id}), 200


@bp.route('/delete_task/<id>', methods=['DELETE'])
def delete_task(id):
    is_success = db_operations.delete_task_by_id(id)
    if is_success:
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', "message": "Task not found"}),  404


@bp.route('/download/<path:filepath>')
def download_file(filepath):
    if current_app.config["UPLOAD_FOLDER"] not in filepath:
        return jsonify({'status': 'error', "message":  f"Permission to download file {filepath} denied"}), 403
    return send_from_directory("./", filepath, as_attachment=True)


@bp.route('/get_video/<path:filepath>')
def get_video(filepath):
    if current_app.config["UPLOAD_FOLDER"] not in filepath:
        return jsonify({'status': 'error', "message":  f"Permission to download file {filepath} denied"}), 403
    return send_from_directory("./", filepath)


@bp.route("/get_json_subs/<task_id>",  methods=["GET"])
def get_json_subs(task_id):
    task = db_operations.get_task_by_id(task_id)
    if task is None:
        return jsonify({'status': 'error', "message":  "Task not found"}), 404
    subs_path = task.json_translated_subs_path
    if subs_path == "":
        return jsonify({'status': 'error', "message":  "No subs for this task"}), 404
        
    try:
        subs_arr = parse_json_to_subtitles(subs_path)
        json_subs = convert_subtitles_to_json_arr(subs_arr)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'Subtitles file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400

    return jsonify({'status': 'success', 'json_subs': json_subs}), 200
    
    
@bp.route("/save_subs/<task_id>", methods=["POST"])
async def save_subs(task_id):
    try:
        new_subs = request.json.get('json_subs')
        if new_subs is None:
            return jsonify({'status': 'error', 'message': 'No subtitles provided'}), 400
        is_valid = validate_json_subs_format(new_subs)

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
        logger.error(err_message)
        # db_operations.set_task_voice_generation_status(task_id=task_id, status=TaskStatus.IDLE)
        return jsonify({'status': 'error', 'message': err_message}), 500

    return jsonify({'status': 'success'}), 202
    
    
@bp.route("/create_subs", methods=["POST"])
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
        
        db_operations.set_task_src_vid_path(task_id, vid_filepath)
        db_operations.set_task_languages(task_id, lang_from, lang_to)
        
        subs_task_item = SubsGenQueueItem(
            task_id=task_id,
            vid_filepath=vid_filepath,
            lang_from=lang_from,
            lang_to=lang_to
        )
        rabbitmq_client.add_task_to_subs_gen_queue(subs_task_item)

        return  jsonify({'status': 'success'}), 202
    except Exception as e:
        logger.error(str(e))
        # db_operations.set_task_subs_generation_status(task_id=task_id, status=TaskStatus.IDLE)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route("/generate_voice/<task_id>", methods=["POST"])
def generate_voice(task_id):
    try:
        task = db_operations.get_task_by_id(task_id)
        if task is None:
            return jsonify({'status': 'error', 'message': 'Task not found'}), 404

        subs_path = task.json_translated_subs_path
        if not subs_path:
            return jsonify({'status': 'error', 'message': 'No subs path for this task'}), 404

        voice_task_item = VoiceGenQueueItem(
            task_id=task_id,
            src_audio_path=task.src_audio_path,
            src_video_path=task.src_vid_path,
            json_subs_path=task.json_translated_subs_path,
            lang_to=task.lang_to
            )

        rabbitmq_client.add_task_to_voice_gen_queue(voice_task_item)
        
    except Exception as e:
        err_message = str(e)
        logger.error(err_message)
        # db_operations.set_task_voice_generation_status(task_id=task_id, status=TaskStatus.IDLE)
        return jsonify({'status': 'error', 'message': err_message}), 500

    return jsonify({'status': 'success'}), 202
