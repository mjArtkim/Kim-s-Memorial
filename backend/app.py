from flask import Flask, request, jsonify, send_from_directory
import os
import sqlite3
import datetime

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')

# Determine project root (parent of 'backend' where this file resides)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define Data and Photo directories relative to Project Root
DATA_DIR = os.path.join(BASE_DIR, 'data')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
DB_PATH = os.path.join(DATA_DIR, 'guestbook.db')

# Admin Credentials
ADMIN_ID = "vonhoon"
ADMIN_PASS = "Peace8111!"

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create table if not exists (original schema)
    c.execute('''CREATE TABLE IF NOT EXISTS guestbook
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, content TEXT, timestamp DATETIME)''')
    
    # Check if 'visible' column exists, if not add it
    c.execute("PRAGMA table_info(guestbook)")
    columns = [info[1] for info in c.fetchall()]
    if 'visible' not in columns:
        print("Migrating database: Adding 'visible' column")
        c.execute("ALTER TABLE guestbook ADD COLUMN visible INTEGER DEFAULT 1")
        
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory(app.static_folder, 'admin.html')

# Catch-all for Vue Router history mode or other static files
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
        # Only show visible entries
        c.execute("SELECT id, name, content, timestamp FROM guestbook WHERE visible = 1 ORDER BY id DESC")
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
            
        c.execute("INSERT INTO guestbook (name, content, timestamp, visible) VALUES (?, ?, ?, 1)", 
                  (name, content, datetime.datetime.now()))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/gallery')
def gallery():
    if not os.path.exists(PHOTOS_DIR):
        return jsonify([])
    
    files = os.listdir(PHOTOS_DIR)
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
    return send_from_directory(PHOTOS_DIR, filename)

# --- Admin API ---

def check_auth(data):
    return data.get('id') == ADMIN_ID and data.get('password') == ADMIN_PASS

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if check_auth(data):
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/admin/guestbook', methods=['POST'])
def admin_guestbook_list():
    # Only authenticated users can see hidden entries
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, content, timestamp, visible FROM guestbook ORDER BY id DESC")
    rows = c.fetchall()
    messages = [{'id': r[0], 'name': r[1], 'content': r[2], 'created_at': r[3], 'visible': r[4]} for r in rows]
    conn.close()
    return jsonify(messages)

@app.route('/api/admin/guestbook/<int:msg_id>/toggle', methods=['POST'])
def admin_guestbook_toggle(msg_id):
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 401
    
    visible_state = data.get('visible') # 1 or 0
    if visible_state is None:
         return jsonify({'error': 'Missing visible state'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE guestbook SET visible = ? WHERE id = ?", (visible_state, msg_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    # Auth check via form fields or headers is trickier with multipart. 
    # For simplicity, we'll check fields if possible, or assume basic auth for this simple app.
    # But files are sent as multipart/form-data.
    # Let's expect auth in form data as well.
    
    auth_id = request.form.get('id')
    auth_pass = request.form.get('password')
    
    if not (auth_id == ADMIN_ID and auth_pass == ADMIN_PASS):
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower() # .jpg
        
        # Determine new filename
        if not os.path.exists(PHOTOS_DIR):
            os.makedirs(PHOTOS_DIR)
            
        existing_files = os.listdir(PHOTOS_DIR)
        max_num = 0
        for f in existing_files:
            try:
                # Expecting format "number.ext"
                base = os.path.splitext(f)[0]
                num = int(base)
                if num > max_num:
                    max_num = num
            except ValueError:
                pass # Ignore non-numeric filenames
        
        new_filename = f"{max_num + 1}{ext}"
        file.save(os.path.join(PHOTOS_DIR, new_filename))
        return jsonify({'success': True, 'filename': new_filename})

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=7554)
