from flask import Flask, Response, render_template, request, redirect, url_for, session, flash, send_from_directory
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

mysql = MySQL(app)

# Секретный ключ для сессий
app.secret_key = 'supersecretkey'

def allowed_file_vid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_VID']

def allowed_file_subs(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_SUBS']

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
    session.pop('loggedin', None)
    session.pop('username', None)
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
    if file and allowed_file_vid(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        session['vid_filename'] = file.filename
        return redirect(url_for('home'))
    else:
        flash('Invalid file type')
        return redirect(url_for('home'))


@app.route('/upload_srt_for_trans', methods=['POST'])
def upload_subs_for_translation():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    if file and allowed_file_subs(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        session['subs_filename'] = file.filename
        return redirect(url_for('home'))
    else:
        flash('Invalid file type')
        return redirect(url_for('home'))
    


@app.route('/create_subs', methods=['POST'])
def create_subs():
    if 'vid_filename' in session:
        filename = session['vid_filename']

        vid_src_lang = request.form.get('vid_src_lang', 'en')
        session['vid_src_lang'] = vid_src_lang

        subs_filename = filename.rsplit('.', 1)[0] + "_subs.srt"
        subs_filepath = os.path.join(app.config['UPLOAD_FOLDER'], subs_filename)
        
        web_app_func.create_subs_from_video(
            in_file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename), 
            out_file_path=subs_filepath, 
            src_lang=session['vid_src_lang']
            )
        session['subs_generated_filename'] = subs_filename
        session['subs_generated_filepath'] = subs_filepath
        return redirect(url_for('home'))
    else:
        flash('No file uploaded')
        return redirect(url_for('home'))

@app.route('/translate_subs', methods=['POST'])
def translate_subs():
    if 'subs_filename' in session:
        filename = session['subs_filename']

        trans_src_lang = request.form.get('trans_src_lang', 'en')
        trans_targ_lang = request.form.get('trans_targ_lang', 'ru')
        session['trans_src_lang'] = trans_src_lang
        session['trans_targ_lang'] = trans_targ_lang

        translated_subs_filename = filename.rsplit('.', 1)[0] + f"_translated_{trans_targ_lang}.srt"
        translated_subs_filepath = os.path.join(app.config['UPLOAD_FOLDER'], translated_subs_filename)
        
        web_app_func.translate_subs(in_file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                    out_file_path=translated_subs_filepath,
                                    src_lang=trans_src_lang,
                                    targ_lang=trans_targ_lang
                                    )
        session['trans_subs_filename'] = translated_subs_filename
        session['trans_subs_filepath'] = translated_subs_filepath
        return redirect(url_for('home'))
    else:
        flash('No file uploaded')
        return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
