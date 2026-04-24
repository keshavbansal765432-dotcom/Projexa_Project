from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import base64
import datetime
from werkzeug.utils import secure_filename

# Modular components
import app_database as db
import app_login as auth
import app_model as model
import app_export as export

# Pathing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

app = Flask(__name__, 
            template_folder=os.path.join(ROOT_DIR, 'templates'), 
            static_folder=os.path.join(ROOT_DIR, 'static'))
app.secret_key = 'skinalyse_keshav_rtx3050'

UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Path to the actual model file
MODEL_PATH = os.path.join(ROOT_DIR, 'skin_model_v2.h5')

# Initialize Services
db.init_db()
firebase = auth.FirebaseAuth()
skin_ai = model.SkinModel(MODEL_PATH)

# Initial Load Attempt
skin_ai.load_model()

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # RELOAD CHECK: If model isn't loaded, try one last time before failing
    if skin_ai.model is None:
        print("[!] Model was missing, attempting emergency reload...")
        skin_ai.load_model()
        if skin_ai.model is None:
            return jsonify({"result": "Error (Model file not found or corrupted)"}), 500

    filepath = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.datetime.now().timestamp()}_{filename}")
            file.save(filepath)
    
    elif request.is_json:
        data = request.get_json()
        if 'image' in data:
            img_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
            filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as fh:
                fh.write(base64.b64decode(img_data))
    
    if filepath:
        # Prediction
        prediction_data = skin_ai.predict(filepath)
        
        # Logic to handle both (label, conf) tuples or single strings
        if isinstance(prediction_data, tuple):
            result_str = f"{prediction_data[0]} ({prediction_data[1]})"
        else:
            result_str = str(prediction_data)

        db.save_result(session['user'], filepath, result_str)
        session['last_result'] = result_str
        session['last_image'] = filepath
        
        return jsonify({"result": result_str, "image": os.path.basename(filepath)})

    return jsonify({"error": "No image provided"}), 400

@app.route('/download_report')
def download_report():
    if 'user' not in session or 'last_result' not in session:
        return redirect(url_for('index'))
    
    report_name = f"Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = os.path.join(UPLOAD_FOLDER, report_name)
    export.generate_pdf_report(session['user'], session['last_result'], session['last_image'], report_path)
    return send_file(report_path, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, pw = request.form.get('email'), request.form.get('password')
        user, err = firebase.sign_in(email, pw)
        if user:
            session['user'] = email
            return redirect(url_for('index'))
        return render_template('login.html', error=err)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match!")

        # Call the Firebase Logic
        user, error = firebase.sign_up(email, password)
        
        if user:
            # Successfully created - redirect to login with a message
            return render_template('login.html', message="Account created! Please verify your email before logging in.")
        else:
            # Firebase returned an error (e.g., EMAIL_EXISTS)
            return render_template('register.html', error=error)
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)