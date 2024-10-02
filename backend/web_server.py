import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
from config import ConfigWeb
from database.models import User, db

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


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Invalid file'}), 400

    file = request.files['file']
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run(debug=False)