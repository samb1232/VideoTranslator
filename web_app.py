from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mysqldb import MySQL
import web_app_func
import os

app = Flask(__name__)

# Конфигурация MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flask_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

# Конфигурация для загрузки файлов
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS_VID'] = {'mp4'}
app.config['ALLOWED_EXTENSIONS_SUBS'] = {"srt"}
app.config['ALLOWED_EXTENSIONS_AUDIO'] = {"wav"}

mysql = MySQL(app)

# Секретный ключ для сессий
app.secret_key = 'supersecretkey'


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def upload_file(file, allowed_extensions, session_key):
    if file and allowed_file(file.filename, allowed_extensions):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        session[session_key] = file.filename
        session[f'{session_key}_filepath'] = filepath
        return True
    else:
        flash('Invalid file type')
        return False


@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/upload_vid', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    if upload_file(file, app.config['ALLOWED_EXTENSIONS_VID'], 'vid_filename'):
        session['extract_subs_status'] = 'unused'
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'})


@app.route('/upload_srt_for_trans', methods=['POST'])
def upload_subs_for_translation():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    if upload_file(file, app.config['ALLOWED_EXTENSIONS_SUBS'], 'subs_filename'):
        session['translate_subs_status'] = 'unused'
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'})

 
@app.route('/upload_srt_for_voice_gen', methods=['POST'])
def upload_subs_for_voice_generation():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    if upload_file(file, app.config['ALLOWED_EXTENSIONS_SUBS'], 'subs_to_voice_gen_filename'):
        session['generate_voice_status'] = 'unused'
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'})
    
 
@app.route('/upload_speaker_example', methods=['POST'])
def upload_speaker_example():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    if upload_file(file, app.config['ALLOWED_EXTENSIONS_AUDIO'], 'speaker_example_filename'):
        session['generate_voice_status'] = 'unused'
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'})
    

@app.route('/create_subs', methods=['POST'])
def create_subs():
    if 'vid_filename' in session:
        session['extract_subs_status'] = 'processing'
        filename = session['vid_filename']
        vid_src_lang = request.form.get('vid_src_lang', 'en')
        session['vid_src_lang'] = vid_src_lang
        subs_filename = filename.rsplit('.', 1)[0] + "_subs.srt"
        subs_filepath = os.path.join(app.config['UPLOAD_FOLDER'], subs_filename)
        try:
            web_app_func.create_subs_from_video(
                in_file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                out_file_path=subs_filepath,
                src_lang=session['vid_src_lang']
            )
            session['subs_generated_filename'] = subs_filename
            session['subs_generated_filepath'] = subs_filepath
            session['extract_subs_status'] = 'done'
            return jsonify({'status': 'success', 'filename': subs_filename})
        except Exception as e:
            session['extract_subs_status'] = 'error'
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})
    

@app.route('/translate_subs', methods=['POST'])
def translate_subs():
    if 'subs_filename' in session:
        session['translate_subs_status'] = 'processing'
        filename = session['subs_filename']
        trans_src_lang = request.form.get('trans_src_lang', 'en')
        trans_targ_lang = request.form.get('trans_targ_lang', 'ru')
        session['trans_src_lang'] = trans_src_lang
        session['trans_targ_lang'] = trans_targ_lang
        translated_subs_filename = filename.rsplit('.', 1)[0] + f"_translated_{trans_targ_lang}.srt"
        translated_subs_filepath = os.path.join(app.config['UPLOAD_FOLDER'], translated_subs_filename)
        try:
            web_app_func.translate_subs(
                in_file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                out_file_path=translated_subs_filepath,
                src_lang=trans_src_lang,
                targ_lang=trans_targ_lang
            )
            session['trans_subs_filename'] = translated_subs_filename
            session['trans_subs_filepath'] = translated_subs_filepath
            session['translate_subs_status'] = 'done'
            return url_for('home')
        except Exception as e:
            session['translate_subs_status'] = 'error'
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})


@app.route('/generate_voice', methods=['POST'])
def generate_voice():
    if 'subs_to_voice_gen_filename' in session and 'speaker_example_filename' in session:
        session['generate_voice_status'] = 'processing'
        speaker_filepath =  os.path.join(app.config['UPLOAD_FOLDER'], session['speaker_example_filename'])

        subs_filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['subs_to_voice_gen_filename'])
        src_lang = request.form.get('voice_src_lang', 'en')
        session['voice_src_lang'] = src_lang
        subs_filename = session['subs_to_voice_gen_filename']
        out_audio_filename = subs_filename.rsplit('.', 1)[0] + ".wav"
        out_audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], out_audio_filename)
        try:
            web_app_func.generate_voice(
                src_lang=src_lang,
                speaker_ex_filepath=speaker_filepath,
                subs_filepath=subs_filepath,
                out_filepath=out_audio_filepath
            )
            session['generated_voice_filename'] = out_audio_filename
            session['generate_voice_status'] = 'done'
            return jsonify({'status': 'success', 'filename': out_audio_filename})
        except Exception as e:
            session['generate_voice_status'] = 'error'
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=False)
