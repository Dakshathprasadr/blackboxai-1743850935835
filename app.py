from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db
from flask_migrate import Migrate
from chatbot import process_message, analyze_symptoms

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

from flask import flash

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        if not check_password_hash(user['password_hash'], password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
            
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username or email already exists!')
            return redirect(url_for('signup'))
        finally:
            conn.close()
            
        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/doctors')
def doctors():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Sample doctor data - in real app this would come from database
    doctors = [
        {'name': 'Dr. Smith', 'specialty': 'Cardiologist', 'availability': 'Mon-Fri, 9am-5pm'},
        {'name': 'Dr. Johnson', 'specialty': 'Pediatrician', 'availability': 'Tue-Sat, 10am-6pm'},
        {'name': 'Dr. Williams', 'specialty': 'Dermatologist', 'availability': 'Mon-Wed, 8am-4pm'},
        {'name': 'Dr. Brown', 'specialty': 'Neurologist', 'availability': 'Thu-Sun, 11am-7pm'},
        {'name': 'Dr. Jones', 'specialty': 'Orthopedist', 'availability': 'Mon-Fri, 9am-5pm'},
        {'name': 'Dr. Garcia', 'specialty': 'General Practitioner', 'availability': 'Mon-Sat, 8am-8pm'}
    ]
    
    return render_template('doctors.html', doctors=doctors)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Process appointment booking
        doctor_id = request.form.get('doctor')
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')
        
        # Save to database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO appointments (user_id, doctor_id, date, time) VALUES (?, ?, ?, ?)',
            (session['user_id'], doctor_id, date, time)
        )
        conn.commit()
        conn.close()
        
        flash('Appointment booked successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('appointment.html')

from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    message = data.get('message', '')
    
    response = process_message(message)
    
    # Save chat log
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO chat_logs (user_id, message, response) VALUES (?, ?, ?)',
        (session['user_id'], message, response)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'response': response})

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # In a real app, you would process the image with a ML model here
        # For now, we'll return a mock response
        return jsonify({
            'injury_type': 'cut',
            'first_aid': 'Clean the wound with water and apply antibiotic ointment.',
            'severity': 'moderate',
            'image_path': filepath
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
