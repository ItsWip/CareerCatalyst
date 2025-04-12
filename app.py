import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, session
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "career_compass_dev_key")

# Mock database for now (will be replaced with proper database integration)
users = {}
profiles = {}
job_listings = []
hackathon_listings = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['user_id'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username in users:
            flash('Username already exists!', 'danger')
        else:
            users[username] = {
                'email': email,
                'password': password,
                'created_at': datetime.now()
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_profile = profiles.get(user_id, {})
    
    return render_template('dashboard.html', profile=user_profile)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        profiles[user_id] = {
            'full_name': request.form.get('full_name'),
            'headline': request.form.get('headline'),
            'summary': request.form.get('summary'),
            'skills': request.form.get('skills', '').split(','),
            'updated_at': datetime.now()
        }
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    user_profile = profiles.get(user_id, {})
    return render_template('profile/view.html', profile=user_profile)

@app.route('/resume')
def resume():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    return render_template('resume/generator.html')

@app.route('/interview')
def interview():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    return render_template('interview/practice.html')

@app.route('/opportunities')
def opportunities():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    return render_template('opportunities/jobs.html', jobs=job_listings)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# Add some sample job listings
job_listings.append({
    'title': 'Python Developer',
    'company': 'Tech Solutions Inc.',
    'location': 'San Francisco, CA',
    'description': 'Developing backend services using Python and Flask.',
    'posted_date': '2023-03-15'
})

job_listings.append({
    'title': 'Data Scientist',
    'company': 'AI Analytics',
    'location': 'Remote',
    'description': 'Analyzing data and building ML models for predictive analytics.',
    'posted_date': '2023-03-10'
})

# Add sample hackathon listings
hackathon_listings.append({
    'name': 'CodeFest 2023',
    'organizer': 'TechHub',
    'location': 'Online',
    'start_date': '2023-04-15',
    'end_date': '2023-04-17',
    'description': 'Build innovative solutions for sustainable development.'
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)