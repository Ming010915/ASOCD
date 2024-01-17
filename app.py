from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
import sqlite3
import os
import atexit

app = Flask(__name__)

# Specify the desired directory and file name
IMAGES_FOLDER_PATH = r""
DB_DIRECTORY = r""
DATABASE_FILE = 'feedback_data.db'
TABLE_NAME = 'feedback'

def get_db_connection():
    return sqlite3.connect(os.path.join(DB_DIRECTORY, DATABASE_FILE))

def create_table():
    with get_db_connection() as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT,
                score INTEGER,
                comments TEXT,
                username TEXT,
                hard BOOLEAN,
                question INTEGER
            )
        ''')

def write_to_sqlite(entry):
    with get_db_connection() as conn:
        conn.execute(f'''
            INSERT INTO {TABLE_NAME} (image_name, score, comments, username, hard, question)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (entry['image_name'], entry["score"], entry['comments'], entry['username'], entry['hard'], entry['question']))

def delete_uncompleted_entries():
    with get_db_connection() as conn:
        conn.execute(f'''
            DELETE FROM {TABLE_NAME}
            WHERE image_name NOT IN (
                SELECT DISTINCT image_name
                FROM {TABLE_NAME}
                WHERE question = 6
            );
        ''')
        
username = ""
create_table()

@app.route('/list_of_images')
def number_of_images():
    image_files = [f for f in os.listdir(IMAGES_FOLDER_PATH) if os.path.isfile(os.path.join(IMAGES_FOLDER_PATH, f))]
    
    message = {
        "image_files": image_files,
    }
    
    return jsonify(message)

@app.route('/get_used_images')
def get_used_images():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT DISTINCT image_name FROM {TABLE_NAME} WHERE username = ?
        ''', (username,))
        used_images = cursor.fetchall()
        processed_data = [item[0] for item in used_images]
        cursor.execute(f'''
            SELECT DISTINCT image_name
            FROM {TABLE_NAME}
            GROUP BY image_name
            HAVING COUNT(DISTINCT username) >= 3;
        ''')
        repeated_images = cursor.fetchall()
        processed_repeated_data = [item[0] for item in repeated_images]
        processed_data = list(set(processed_data + processed_repeated_data))
        return jsonify(processed_data)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record_data', methods=['POST'])
def record_data():
    imageName = request.form.get('imageName')
    parts = imageName.split("/images/")
    parts.pop(0)
    
    comments = request.form.get('comments')
    username = request.form.get('username')
    score = request.form.get('score')
    hard = request.form.get('hard')
    question = request.form.get('question')

    entry = {'image_name': parts[0], 'score': score, 'comments': comments, 'username': username, 'hard': hard, 'question': question}
    write_to_sqlite(entry)  
    return redirect(url_for('index'))

@app.route('/current_user', methods=['POST'])
def current_user():
    global username 
    username = request.form.get('username')
    return username

@app.route('/delete_data', methods=['POST'])
def delete_data():
    imageName = request.form.get('imageName')
    result = imageName.split("/images/")
    result.pop(0)

    username = request.form.get('username')        
    with get_db_connection() as conn:
        conn.execute(f'''
            DELETE FROM {TABLE_NAME}
            WHERE image_name = ? AND username = ?
        ''', (result[0], username,)
        )
    return redirect(url_for('index'))

@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(IMAGES_FOLDER_PATH, filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

atexit.register(delete_uncompleted_entries)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')