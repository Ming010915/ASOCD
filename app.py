from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import atexit

app = Flask(__name__)

username = ""
app.config['DATABASE'] = 'feedback_data.db'

def get_db_connection():
    return sqlite3.connect(app.config['DATABASE'])

def create_table():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback_data (
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
        conn.execute('''
            INSERT INTO feedback_data (image_name, score, comments, username, hard, question)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (entry['image_name'], entry["score"], entry['comments'], entry['username'], entry['hard'], entry['question']))
    
create_table()

@app.route('/number_of_images')
def number_of_images():
    # Specify the path to your images folder
    images_folder_path = 'static/images'

    # Get the list of files in the folder
    image_files = [f for f in os.listdir(images_folder_path) if os.path.isfile(os.path.join(images_folder_path, f))]
    
    message = {
        "image_files": image_files,
        "length": len(image_files)
    }
    
    return jsonify(message)

@app.route('/get_used_images')
def get_used_images():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT image_name FROM feedback_data WHERE username = ?
        ''', (username,))
        used_images = cursor.fetchall()
        processed_data = [item[0] for item in used_images]
        cursor.execute('''
            SELECT DISTINCT image_name
            FROM feedback_data
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
    comments = request.form.get('comments')
    image_name = request.form.get('imageName')
    parts = image_name.split("/")

    # Find the index of "images" in the parts list
    index = parts.index("images")

    # Get the substring after "images/"
    result = "/".join(parts[index + 1:])
    username = request.form.get('username')
    score = request.form.get('score')
    hard = request.form.get('hard')
    question = request.form.get('question')

    entry = {'image_name': result, 'score': score, 'comments': comments, 'username': username, 'hard': hard, 'question': question}
    write_to_sqlite(entry)  
    return redirect(url_for('index'))

@app.route('/current_user', methods=['POST'])
def current_user():
    global username 
    username = request.form.get('username')
    return username

def delete_uncompleted_entries():
    with get_db_connection() as conn:
        conn.execute('''
            DELETE FROM feedback_data
            WHERE image_name NOT IN (
                SELECT DISTINCT image_name
                FROM feedback_data
                WHERE question = 6
            );
        ''')

@app.route('/delete_data', methods=['POST'])
def delete_data():
    imageName1 = request.form.get('imageName')
    username1 = request.form.get('username')

    parts = imageName1.split("/")

    # Find the index of "images" in the parts list
    index = parts.index("images")

    # Get the substring after "images/"
    result = "/".join(parts[index + 1:])
        
    with get_db_connection() as conn:
        conn.execute('''
            DELETE FROM feedback_data
            WHERE image_name = ? AND username = ?
        ''', (result, username1,)
        )
    return redirect(url_for('index'))

atexit.register(delete_uncompleted_entries)

if __name__ == '__main__':
    app.run(debug=True)