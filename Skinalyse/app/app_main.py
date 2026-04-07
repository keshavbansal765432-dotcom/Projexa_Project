from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import base64
import datetime
from werkzeug.utils import secure_filename

# Importing your modular components
import app_database as db
import app_login as auth
import app_model as model
import app_export as export

# --- PATH CONFIGURATION ---
# BASE_DIR is the 'app' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR is the 'SKINALYSE' folder
ROOT_DIR = os.path.dirname(BASE_DIR)

app = Flask(__name__, 
            template_folder=os.path.join(ROOT_DIR, 'templates'), 
            static_folder=os.path.join(ROOT_DIR, 'static'))
app.secret_key = 'skinalyse_secret_key'

UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODEL_PATH = os.path.join(ROOT_DIR, 'skin_model.h5')

# --- INITIALIZE SERVICES ---
db.init_db()
firebase = auth.FirebaseAuth()
skin_ai = model.SkinModel(MODEL_PATH)

# Attempt to load model on startup
status, msg = skin_ai.load_model()
print(f"[*] Model Status: {msg}")

@app.route('/')
def index():
    if 'user' in session:
        result = request.args.get('result') or session.get('last_result')
        image = request.args.get('image') or (os.path.basename(session.get('last_image')) if session.get('last_image') else None)
        return render_template('index.html', user=session['user'], result=result, image=image)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user, error = firebase.sign_in(email, password)
        if user:
            session['user'] = email
            db.save_user(email, user['localId'])
            return redirect(url_for('index'))
        return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user, error = firebase.sign_up(email, password)
        if user:
            return render_template('login.html', message="Verification email sent!")
        return render_template('register.html', error=error)
    return render_template('register.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    filepath = None
    
    # Handle File Upload
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.datetime.now().timestamp()}_{filename}")
            file.save(filepath)
    
    # Handle Base64 Camera Capture
    elif request.is_json:
        data = request.get_json()
        if 'image' in data:
            img_data = data['image']
            if ',' in img_data:
                img_data = img_data.split(',')[1]
            
            filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, "wb") as fh:
                fh.write(base64.b64decode(img_data))
    
    if filepath:
        # Run AI Analysis
        result = skin_ai.predict(filepath)
        db.save_result(session['user'], filepath, result)
        
        # Update session for PDF generation
        session['last_result'] = result
        session['last_image'] = filepath
        
        return jsonify({
            "result": result, 
            "image": os.path.basename(filepath)
        })

    return jsonify({"error": "No image data provided"}), 400

@app.route('/download_report')
def download_report():
    if 'user' not in session or 'last_result' not in session:
        return redirect(url_for('index'))
    
    report_filename = f"Skin_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = os.path.join(UPLOAD_FOLDER, report_filename)
    export.generate_pdf_report(session['user'], session['last_result'], session['last_image'], report_path)
    
    return send_file(report_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Running on port 5000 for Parrot Linux local access
    app.run(debug=True, port=5000)