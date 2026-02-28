from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import base64
import datetime
from werkzeug.utils import secure_filename
import app_database as db
import app_login as auth
import app_model as model
import app_export as export

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')
app.secret_key = 'skinalyse_secret_key'

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'skin_model.h5')

# Initialize Services
db.init_db()
firebase = auth.FirebaseAuth()
skin_ai = model.SkinModel(MODEL_PATH)
skin_ai.load_model()

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user, error = firebase.sign_up(email, password)
        if user:
            return render_template('login.html', message="Verification email sent! Please check your inbox.")
        return render_template('signup.html', error=error)
    return render_template('signup.html')

# Handle both File Uploads and Base64 Camera Captures
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    filepath = None
    
    # Option 1: Handle File Upload (Input type="file")
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.datetime.now().timestamp()}_{filename}")
            file.save(filepath)
    
    # Option 2: Handle Base64 Data (from Camera Capture)
    elif request.is_json:
        data = request.get_json()
        if 'image' in data:
            img_data = data['image']
            # Remove header if present (e.g., "data:image/png;base64,")
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
        
        # Store in session for report generation
        session['last_result'] = result
        session['last_image'] = filepath
        
        # Return result (can be used for both page refresh or AJAX)
        if request.is_json:
            return jsonify({"result": result, "image": os.path.basename(filepath)})
        return render_template('index.html', user=session['user'], result=result, image=os.path.basename(filepath))

    return redirect(url_for('index'))

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
    # Start Flask Server
    app.run(debug=True, port=5000)
