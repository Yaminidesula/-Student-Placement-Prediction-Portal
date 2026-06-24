"""
Student Placement Prediction Portal - Flask Application
Main application file with all routes and logic
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import joblib
import numpy as np
import os
from datetime import datetime
import io
import csv

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2005'
app.config['MYSQL_DB'] = 'placement_portal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize MySQL
mysql = MySQL(app)

# Load ML Model
def load_model():
    """Load the trained model and preprocessing objects"""
    try:
        model_data = joblib.load('model.pkl')
        return model_data
    except FileNotFoundError:
        print("Warning: model.pkl not found. Please run train_model.py first.")
        return None

# Global model variable
model_data = None

# Helper Functions
def get_db_connection():
    """Get database connection cursor"""
    return mysql.connection.cursor()

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def get_current_user():
    """Get current logged in user data"""
    if is_logged_in():
        cursor = get_db_connection()
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        return user
    return None

def predict_placement(form_data):
    """
    Make placement prediction using the ML model
    Returns: (result_str, probability_float)
    """
    global model_data
    
    if model_data is None:
        return "Model not loaded", 0.0
    
    model = model_data['model']
    scaler = model_data['scaler']
    label_encoders = model_data['label_encoders']
    
    try:
        # Extract and encode features
        gender = 1 if form_data['gender'] == 'M' else 0
        ssc_p = float(form_data['ssc_p'])
        hsc_p = float(form_data['hsc_p'])
        degree_p = float(form_data['degree_p'])
        mba_p = float(form_data['mba_p'])
        specialisation = 0 if form_data['specialisation'] == 'Mkt&HR' else 1
        workex = 1 if form_data['workex'] == 'Yes' else 0
        
        # Count skills
        skills = form_data.get('skills', '')
        skills_count = len([s.strip() for s in skills.split(',') if s.strip()])
        
        # Create feature array
        features = np.array([[gender, ssc_p, hsc_p, degree_p, mba_p, 
                             specialisation, workex, skills_count]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]
        
        # Get placement probability (probability of class 1 - Placed)
        placement_prob = probability[1] * 100
        
        result = "Placed" if prediction == 1 else "Not Placed"
        
        return result, round(placement_prob, 2)
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error", 0.0

def get_suggested_companies(probability):
    """Get list of suggested companies based on placement probability"""
    companies = []
    
    if probability >= 80:
        companies = ['TCS', 'Infosys', 'Wipro', 'Google', 'Microsoft', 'Amazon']
    elif probability >= 60:
        companies = ['TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture']
    elif probability >= 40:
        companies = ['TCS', 'Wipro', 'Cognizant']
    else:
        companies = ['Wipro', 'Startups', 'Small IT Companies']
    
    return companies

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page with statistics"""
    if not is_logged_in():
        flash('Please login to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = get_current_user()
    cursor = get_db_connection()
    
    # Get user's prediction statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_predictions,
            SUM(CASE WHEN result = 'Placed' THEN 1 ELSE 0 END) as placed_count,
            AVG(probability) as avg_probability
        FROM predictions 
        WHERE user_id = %s
    """, (session['user_id'],))
    
    stats = cursor.fetchone()
    cursor.close()
    
    # Calculate placement rate
    total = stats['total_predictions'] or 0
    placed = stats['placed_count'] or 0
    placement_rate = round((placed / total * 100), 1) if total > 0 else 0
    avg_prob = round(stats['avg_probability'], 1) if stats['avg_probability'] else 0
    
    return render_template('dashboard.html', 
                         user=user, 
                         total_predictions=total,
                         placed_count=placed,
                         placement_rate=placement_rate,
                         avg_probability=avg_prob)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = get_db_connection()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        branch = request.form.get('branch', '')
        roll_number = request.form.get('roll_number', '')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('register.html')
        
        cursor = get_db_connection()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered', 'danger')
            cursor.close()
            return render_template('register.html')
        
        # Handle profile photo upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                profile_photo = filename
        
        # Hash password and insert user with Student role
        hashed_password = generate_password_hash(password)
        role = 'Student'  # Default role for all users
        cursor.execute(
            "INSERT INTO users (name, email, password, profile_photo, branch, roll_number, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, email, hashed_password, profile_photo, branch, roll_number, role)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Prediction form page"""
    if not is_logged_in():
        flash('Please login to make predictions', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        form_data = {
            'gender': request.form['gender'],
            'ssc_p': request.form['ssc_p'],
            'hsc_p': request.form['hsc_p'],
            'degree_p': request.form['degree_p'],
            'mba_p': request.form['mba_p'],
            'specialisation': request.form['specialisation'],
            'workex': request.form['workex'],
            'skills': request.form['skills']
        }
        
        # Make prediction
        result, probability = predict_placement(form_data)
        
        if result == "Error":
            flash('Error making prediction. Please try again.', 'danger')
            return redirect(url_for('predict'))
        
        # Store prediction in database
        cursor = get_db_connection()
        cursor.execute("""
            INSERT INTO predictions 
            (user_id, gender, tenth_percentage, twelfth_percentage, degree_percentage, 
             mba_percentage, specialization, work_experience, skills, result, probability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            form_data['gender'],
            form_data['ssc_p'],
            form_data['hsc_p'],
            form_data['degree_p'],
            form_data['mba_p'],
            form_data['specialisation'],
            form_data['workex'],
            form_data['skills'],
            result,
            probability
        ))
        mysql.connection.commit()
        prediction_id = cursor.lastrowid
        cursor.close()
        
        # Redirect to result page
        return redirect(url_for('result', prediction_id=prediction_id))
    
    return render_template('form.html')

@app.route('/result/<int:prediction_id>')
def result(prediction_id):
    """Prediction result page"""
    if not is_logged_in():
        flash('Please login to view results', 'warning')
        return redirect(url_for('login'))
    
    cursor = get_db_connection()
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE id = %s AND user_id = %s
    """, (prediction_id, session['user_id']))
    
    prediction = cursor.fetchone()
    cursor.close()
    
    if not prediction:
        flash('Prediction not found', 'danger')
        return redirect(url_for('history'))
    
    # Get suggested companies
    companies = get_suggested_companies(prediction['probability'])
    
    return render_template('result.html', prediction=prediction, companies=companies)

@app.route('/profile')
def profile():
    """User profile page"""
    if not is_logged_in():
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('login'))
    
    user = get_current_user()
    
    cursor = get_db_connection()
    cursor.execute("""
        SELECT COUNT(*) as total FROM predictions WHERE user_id = %s
    """, (session['user_id'],))
    prediction_count = cursor.fetchone()['total']
    cursor.close()
    
    return render_template('profile.html', user=user, prediction_count=prediction_count)

@app.route('/history')
def history():
    """Prediction history page"""
    if not is_logged_in():
        flash('Please login to view history', 'warning')
        return redirect(url_for('login'))
    
    cursor = get_db_connection()
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    
    predictions = cursor.fetchall()
    cursor.close()
    
    return render_template('history.html', predictions=predictions)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/export_report')
def export_report():
    """Export prediction history as CSV"""
    if not is_logged_in():
        flash('Please login to export reports', 'warning')
        return redirect(url_for('login'))
    
    cursor = get_db_connection()
    
    # Get user details
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    # Get predictions
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    predictions = cursor.fetchall()
    cursor.close()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Student Placement Prediction Report'])
    writer.writerow([])
    writer.writerow(['Student Name:', user['name']])
    writer.writerow(['Email:', user['email']])
    writer.writerow(['Branch:', user.get('branch', 'N/A')])
    writer.writerow(['Roll Number:', user.get('roll_number', 'N/A')])
    writer.writerow(['Report Generated:', datetime.now().strftime('%d %B %Y at %H:%M')])
    writer.writerow([])
    
    # Write predictions table
    writer.writerow(['Prediction History'])
    writer.writerow(['#', 'Date', 'Gender', '10th %', '12th %', 'Degree %', 'MBA %', 
                     'Specialization', 'Work Exp', 'Skills', 'Result', 'Probability'])
    
    for idx, pred in enumerate(predictions, 1):
        writer.writerow([
            idx,
            pred['created_at'].strftime('%d %b %Y %H:%M'),
            pred['gender'],
            pred['tenth_percentage'],
            pred['twelfth_percentage'],
            pred['degree_percentage'],
            pred['mba_percentage'],
            pred['specialization'],
            pred['work_experience'],
            pred['skills'][:50] + '...' if len(pred['skills']) > 50 else pred['skills'],
            pred['result'],
            f"{pred['probability']}%"
        ])
    
    writer.writerow([])
    writer.writerow(['Summary'])
    total = len(predictions)
    placed = sum(1 for p in predictions if p['result'] == 'Placed')
    writer.writerow(['Total Predictions:', total])
    writer.writerow(['Placed:', placed])
    writer.writerow(['Not Placed:', total - placed])
    if total > 0:
        writer.writerow(['Placement Rate:', f"{(placed/total*100):.1f}%"])
        avg_prob = sum(p['probability'] for p in predictions) / total
        writer.writerow(['Average Probability:', f"{avg_prob:.1f}%"])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'placement_report_{user["name"].replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('base.html', error="Internal server error"), 500

# Context processor for template variables
@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'app_name': 'Student Placement Prediction Portal',
        'college_name': 'JNTU-GV Vizianagaram',
        'current_year': datetime.now().year
    }

# Initialize model on startup
with app.app_context():
    model_data = load_model()
    if model_data:
        print("ML Model loaded successfully!")
    else:
        print("Warning: ML Model not found. Run train_model.py to create model.pkl")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
