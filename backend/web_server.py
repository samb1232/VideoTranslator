from datetime import datetime
import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
from web_app_func import create_subs_from_video
from config import ConfigWeb
from database.models import Task, User, db

app = Flask(__name__)
app.config.from_object(ConfigWeb)
CORS(app, supports_credentials=True)

server_session = Session(app)

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/@me", methods=["GET"])  
def get_current_user():
    try:
        user_id = session["user_id"]
    except KeyError as e:
        user_id = None
        
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.filter_by(id=user_id).first()
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
    
    user = User.query.filter_by(username=username).first()

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
    if 'video_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Invalid video file'}), 400

    file = request.files['video_file']
    src_lang = request.form["src_lang"]


    if file.filename.split(".")[-1] != "mp4":
        return jsonify({'status': 'error', 'message': 'Invalid video file extension'}), 400
    vid_filepath = upload_file(file)

    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    out_json_filepath, out_srt_filepath, out_audio_filepath = create_subs_from_video(
        in_file_path=vid_filepath,
        out_dir_path= app.config['RESULTS_FOLDER'],
        src_lang=src_lang 
        )
    
    json_filename =  os.path.split(out_json_filepath)[-1]
    srt_filename =  os.path.split(out_srt_filepath)[-1]
    audio_filename =  os.path.split(out_audio_filepath)[-1]

    return  jsonify({
        'status': 'success',
         "json_filename": json_filename, 
         "srt_filename": srt_filename, 
         "audio_filename": audio_filename
         }), 200


@app.route("/get_all_tasks",  methods=["GET"])
def  get_all_tasks():
    tasks_arr = Task.query.order_by(Task.last_used).all()
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
    task: Task = Task.query.filter_by(id=id).first()
    if task is None:
        return jsonify({'status': 'error', "message":  "Task not found"}),  404
    
    return jsonify({'status': 'success', "task_info": task.to_json()}), 200


@app.route("/create_task",  methods=["POST"])
def  create_task():
    request_json = request.json
    title = request_json['title']
    task = Task(
        title=title,
        last_used=datetime.now(),
        creation_date = datetime.now()
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'status': 'success', "task_id":  task.id}), 200


@app.route('/delete_task/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        return jsonify({'status': 'error', "message":  "Task not found"}),  404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'status': 'success'}), 200


def upload_file(file):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return filepath

if __name__ == '__main__':
    app.run(debug=True)