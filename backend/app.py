from flask import Flask, request, jsonify, send_from_directory
import os
import sqlite3
import datetime

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
DB_PATH = 'data/guestbook.db'

def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS guestbook
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, content TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Catch-all for Vue Router history mode
@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api'):
        return "Not Found", 404
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/guestbook', methods=['GET', 'POST'])
def guestbook():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT id, name, content, timestamp FROM guestbook ORDER BY id DESC")
        rows = c.fetchall()
        messages = [{'id': r[0], 'name': r[1], 'content': r[2], 'created_at': r[3]} for r in rows]
        conn.close()
        return jsonify(messages)
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        content = data.get('content')
        if not name or not content:
            conn.close()
            return jsonify({'error': 'Missing name or content'}), 400
            
        c.execute("INSERT INTO guestbook (name, content, timestamp) VALUES (?, ?, ?)", 
                  (name, content, datetime.datetime.now()))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/gallery')
def gallery():
    photos_dir = 'photos'
    if not os.path.exists(photos_dir):
        return jsonify([])
    
    files = os.listdir(photos_dir)
    # Filter for image/video extensions if needed, for now send all files
    # Sorting by name as requested
    # Natural sort (handles 1.jpg, 2.jpg, 10.jpg correctly)
    import re
    def natural_key(text):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]
    files.sort(key=natural_key)
    return jsonify(files)

# Serve photos directly
@app.route('/photos/<path:filename>')
def serve_photos(filename):
    return send_from_directory('photos', filename)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=7554)
