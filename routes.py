from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import io
import os

from app import app, db
from models import (User, Education, Experience, Project, Skill, Certification, 
                   Resume, Interview, InterviewQA, SavedJob, SavedHackathon)
from utils.nlp_utils import extract_keywords, match_skills_with_job
from utils.resume_generator import generate_resume_pdf
from utils.interview_ai import generate_interview_questions, analyze_answer
from utils.job_scraper import search_jobs, search_hackathons
from utils.speech_utils import text_to_speech, speech_to_text

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
            
        flash('Login successful', 'success')
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# User profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        current_user.linkedin = request.form.get('linkedin')
        current_user.github = request.form.get('github')
        current_user.bio = request.form.get('bio')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    educations = Education.query.filter_by(user_id=current_user.id).all()
    experiences = Experience.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    
    return render_template('profile.html', 
                          educations=educations,
                          experiences=experiences,
                          projects=projects,
                          skills=skills,
                          certifications=certifications)

# Education CRUD
@app.route('/education/add', methods=['POST'])
@login_required
def add_education():
    institution = request.form.get('institution')
    degree = request.form.get('degree')
    field_of_study = request.form.get('field_of_study')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    description = request.form.get('description')
    gpa = request.form.get('gpa')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    education = Education(
        user_id=current_user.id,
        institution=institution,
        degree=degree,
        field_of_study=field_of_study,
        start_date=start_date,
        end_date=end_date,
        description=description,
        gpa=float(gpa) if gpa else None
    )
    
    db.session.add(education)
    db.session.commit()
    
    flash('Education added successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/education/edit/<int:id>', methods=['POST'])
@login_required
def edit_education(id):
    education = Education.query.get_or_404(id)
    
    if education.user_id != current_user.id:
        flash('You are not authorized to edit this education entry', 'danger')
        return redirect(url_for('profile'))
    
    education.institution = request.form.get('institution')
    education.degree = request.form.get('degree')
    education.field_of_study = request.form.get('field_of_study')
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    education.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    education.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    education.description = request.form.get('description')
    education.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else None
    
    db.session.commit()
    
    flash('Education updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/education/delete/<int:id>')
@login_required
def delete_education(id):
    education = Education.query.get_or_404(id)
    
    if education.user_id != current_user.id:
        flash('You are not authorized to delete this education entry', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(education)
    db.session.commit()
    
    flash('Education deleted successfully', 'success')
    return redirect(url_for('profile'))

# Experience CRUD
@app.route('/experience/add', methods=['POST'])
@login_required
def add_experience():
    company = request.form.get('company')
    position = request.form.get('position')
    location = request.form.get('location')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    current = True if request.form.get('current') else False
    description = request.form.get('description')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str and not current else None
    
    experience = Experience(
        user_id=current_user.id,
        company=company,
        position=position,
        location=location,
        start_date=start_date,
        end_date=end_date,
        current=current,
        description=description
    )
    
    db.session.add(experience)
    db.session.commit()
    
    flash('Experience added successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/experience/edit/<int:id>', methods=['POST'])
@login_required
def edit_experience(id):
    experience = Experience.query.get_or_404(id)
    
    if experience.user_id != current_user.id:
        flash('You are not authorized to edit this experience entry', 'danger')
        return redirect(url_for('profile'))
    
    experience.company = request.form.get('company')
    experience.position = request.form.get('position')
    experience.location = request.form.get('location')
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    experience.current = True if request.form.get('current') else False
    experience.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    experience.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str and not experience.current else None
    experience.description = request.form.get('description')
    
    db.session.commit()
    
    flash('Experience updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/experience/delete/<int:id>')
@login_required
def delete_experience(id):
    experience = Experience.query.get_or_404(id)
    
    if experience.user_id != current_user.id:
        flash('You are not authorized to delete this experience entry', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(experience)
    db.session.commit()
    
    flash('Experience deleted successfully', 'success')
    return redirect(url_for('profile'))

# Project CRUD
@app.route('/project/add', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    tech_stack = request.form.get('tech_stack')
    github_link = request.form.get('github_link')
    live_link = request.form.get('live_link')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    project = Project(
        user_id=current_user.id,
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        tech_stack=tech_stack,
        github_link=github_link,
        live_link=live_link
    )
    
    db.session.add(project)
    db.session.commit()
    
    flash('Project added successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/project/edit/<int:id>', methods=['POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if project.user_id != current_user.id:
        flash('You are not authorized to edit this project', 'danger')
        return redirect(url_for('profile'))
    
    project.title = request.form.get('title')
    project.description = request.form.get('description')
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    project.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    project.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    project.tech_stack = request.form.get('tech_stack')
    project.github_link = request.form.get('github_link')
    project.live_link = request.form.get('live_link')
    
    db.session.commit()
    
    flash('Project updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/project/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    if project.user_id != current_user.id:
        flash('You are not authorized to delete this project', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully', 'success')
    return redirect(url_for('profile'))

# Skill CRUD
@app.route('/skill/add', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('name')
    level = request.form.get('level')
    category = request.form.get('category')
    
    skill = Skill(
        user_id=current_user.id,
        name=name,
        level=level,
        category=category
    )
    
    db.session.add(skill)
    db.session.commit()
    
    flash('Skill added successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/skill/edit/<int:id>', methods=['POST'])
@login_required
def edit_skill(id):
    skill = Skill.query.get_or_404(id)
    
    if skill.user_id != current_user.id:
        flash('You are not authorized to edit this skill', 'danger')
        return redirect(url_for('profile'))
    
    skill.name = request.form.get('name')
    skill.level = request.form.get('level')
    skill.category = request.form.get('category')
    
    db.session.commit()
    
    flash('Skill updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/skill/delete/<int:id>')
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    
    if skill.user_id != current_user.id:
        flash('You are not authorized to delete this skill', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(skill)
    db.session.commit()
    
    flash('Skill deleted successfully', 'success')
    return redirect(url_for('profile'))

# Certification CRUD
@app.route('/certification/add', methods=['POST'])
@login_required
def add_certification():
    name = request.form.get('name')
    issuing_organization = request.form.get('issuing_organization')
    issue_date_str = request.form.get('issue_date')
    expiry_date_str = request.form.get('expiry_date')
    credential_id = request.form.get('credential_id')
    credential_url = request.form.get('credential_url')
    
    issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date() if issue_date_str else None
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date() if expiry_date_str else None
    
    certification = Certification(
        user_id=current_user.id,
        name=name,
        issuing_organization=issuing_organization,
        issue_date=issue_date,
        expiry_date=expiry_date,
        credential_id=credential_id,
        credential_url=credential_url
    )
    
    db.session.add(certification)
    db.session.commit()
    
    flash('Certification added successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/certification/edit/<int:id>', methods=['POST'])
@login_required
def edit_certification(id):
    certification = Certification.query.get_or_404(id)
    
    if certification.user_id != current_user.id:
        flash('You are not authorized to edit this certification', 'danger')
        return redirect(url_for('profile'))
    
    certification.name = request.form.get('name')
    certification.issuing_organization = request.form.get('issuing_organization')
    
    issue_date_str = request.form.get('issue_date')
    expiry_date_str = request.form.get('expiry_date')
    
    certification.issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date() if issue_date_str else None
    certification.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date() if expiry_date_str else None
    
    certification.credential_id = request.form.get('credential_id')
    certification.credential_url = request.form.get('credential_url')
    
    db.session.commit()
    
    flash('Certification updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/certification/delete/<int:id>')
@login_required
def delete_certification(id):
    certification = Certification.query.get_or_404(id)
    
    if certification.user_id != current_user.id:
        flash('You are not authorized to delete this certification', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(certification)
    db.session.commit()
    
    flash('Certification deleted successfully', 'success')
    return redirect(url_for('profile'))

# Resume routes
@app.route('/resume')
@login_required
def resume():
    educations = Education.query.filter_by(user_id=current_user.id).all()
    experiences = Experience.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    
    return render_template('resume.html',
                          educations=educations,
                          experiences=experiences,
                          projects=projects,
                          skills=skills,
                          certifications=certifications,
                          resumes=resumes)

@app.route('/resume/analyze-job', methods=['POST'])
@login_required
def analyze_job():
    job_description = request.form.get('job_description')
    
    if not job_description or len(job_description) < 50:
        return jsonify({'error': 'Please provide a complete job description (at least 50 characters)'}), 400
    
    # Extract keywords from the job description
    keywords = extract_keywords(job_description)
    
    # Get user skills
    user_skills = [skill.name for skill in Skill.query.filter_by(user_id=current_user.id).all()]
    
    # Match user skills with job requirements
    matched_skills, missing_skills = match_skills_with_job(user_skills, keywords)
    
    return jsonify({
        'keywords': keywords,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills
    })

@app.route('/resume/create', methods=['POST'])
@login_required
def create_resume():
    name = request.form.get('resume_name')
    job_description = request.form.get('job_description')
    template = request.form.get('template')
    
    # Get selected items for inclusion in resume
    education_ids = request.form.getlist('education_ids')
    experience_ids = request.form.getlist('experience_ids')
    project_ids = request.form.getlist('project_ids')
    skill_ids = request.form.getlist('skill_ids')
    certification_ids = request.form.getlist('certification_ids')
    
    # Create a new resume record
    resume = Resume(
        user_id=current_user.id,
        name=name,
        job_description=job_description,
        template_used=template,
        included_education_ids=','.join(education_ids) if education_ids else '',
        included_experience_ids=','.join(experience_ids) if experience_ids else '',
        included_project_ids=','.join(project_ids) if project_ids else '',
        included_skill_ids=','.join(skill_ids) if skill_ids else '',
        included_certification_ids=','.join(certification_ids) if certification_ids else ''
    )
    
    db.session.add(resume)
    db.session.commit()
    
    flash('Resume created successfully', 'success')
    return redirect(url_for('view_resume', id=resume.id))

@app.route('/resume/view/<int:id>')
@login_required
def view_resume(id):
    resume = Resume.query.get_or_404(id)
    
    if resume.user_id != current_user.id:
        flash('You are not authorized to view this resume', 'danger')
        return redirect(url_for('resume'))
    
    # Get user details
    user = User.query.get(current_user.id)
    
    # Get items included in the resume
    educations = []
    if resume.included_education_ids:
        education_ids = [int(id) for id in resume.included_education_ids.split(',')]
        educations = Education.query.filter(Education.id.in_(education_ids)).all()
    
    experiences = []
    if resume.included_experience_ids:
        experience_ids = [int(id) for id in resume.included_experience_ids.split(',')]
        experiences = Experience.query.filter(Experience.id.in_(experience_ids)).all()
    
    projects = []
    if resume.included_project_ids:
        project_ids = [int(id) for id in resume.included_project_ids.split(',')]
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
    
    skills = []
    if resume.included_skill_ids:
        skill_ids = [int(id) for id in resume.included_skill_ids.split(',')]
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
    
    certifications = []
    if resume.included_certification_ids:
        certification_ids = [int(id) for id in resume.included_certification_ids.split(',')]
        certifications = Certification.query.filter(Certification.id.in_(certification_ids)).all()
    
    # Render the appropriate template
    template = f'templates/{resume.template_used}.html'
    
    return render_template(template,
                          resume=resume,
                          user=user,
                          educations=educations,
                          experiences=experiences,
                          projects=projects,
                          skills=skills,
                          certifications=certifications)

@app.route('/resume/download/<int:id>')
@login_required
def download_resume(id):
    resume = Resume.query.get_or_404(id)
    
    if resume.user_id != current_user.id:
        flash('You are not authorized to download this resume', 'danger')
        return redirect(url_for('resume'))
    
    # Get user details
    user = User.query.get(current_user.id)
    
    # Get items included in the resume
    educations = []
    if resume.included_education_ids:
        education_ids = [int(id) for id in resume.included_education_ids.split(',')]
        educations = Education.query.filter(Education.id.in_(education_ids)).all()
    
    experiences = []
    if resume.included_experience_ids:
        experience_ids = [int(id) for id in resume.included_experience_ids.split(',')]
        experiences = Experience.query.filter(Experience.id.in_(experience_ids)).all()
    
    projects = []
    if resume.included_project_ids:
        project_ids = [int(id) for id in resume.included_project_ids.split(',')]
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
    
    skills = []
    if resume.included_skill_ids:
        skill_ids = [int(id) for id in resume.included_skill_ids.split(',')]
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
    
    certifications = []
    if resume.included_certification_ids:
        certification_ids = [int(id) for id in resume.included_certification_ids.split(',')]
        certifications = Certification.query.filter(Certification.id.in_(certification_ids)).all()
    
    # Generate PDF
    pdf_data = generate_resume_pdf(
        template=resume.template_used,
        user=user,
        educations=educations,
        experiences=experiences,
        projects=projects,
        skills=skills,
        certifications=certifications
    )
    
    # Create a response with the PDF
    from flask import send_file
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{user.full_name or user.username}_Resume_{resume.name}.pdf"
    )

@app.route('/resume/delete/<int:id>')
@login_required
def delete_resume(id):
    resume = Resume.query.get_or_404(id)
    
    if resume.user_id != current_user.id:
        flash('You are not authorized to delete this resume', 'danger')
        return redirect(url_for('resume'))
    
    db.session.delete(resume)
    db.session.commit()
    
    flash('Resume deleted successfully', 'success')
    return redirect(url_for('resume'))

# Interview routes
@app.route('/interview')
@login_required
def interview():
    interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.created_at.desc()).all()
    return render_template('interview.html', interviews=interviews)

@app.route('/interview/start', methods=['POST'])
@login_required
def start_interview():
    title = request.form.get('title')
    job_role = request.form.get('job_role')
    interview_type = request.form.get('interview_type')
    mode = request.form.get('mode')
    
    # Create a new interview session
    interview = Interview(
        user_id=current_user.id,
        title=title,
        job_role=job_role,
        interview_type=interview_type,
        mode=mode
    )
    
    db.session.add(interview)
    db.session.commit()
    
    # Generate initial questions based on the selected role and type
    questions = generate_interview_questions(job_role, interview_type, 5)
    
    for question in questions:
        qa = InterviewQA(
            interview_id=interview.id,
            question=question,
            answer=None,
            feedback=None,
            score=None
        )
        db.session.add(qa)
    
    db.session.commit()
    
    # Store the current question index in the session
    session['current_question_index'] = 0
    session['interview_id'] = interview.id
    
    flash('Interview started!', 'success')
    return redirect(url_for('conduct_interview', id=interview.id))

@app.route('/interview/conduct/<int:id>')
@login_required
def conduct_interview(id):
    interview = Interview.query.get_or_404(id)
    
    if interview.user_id != current_user.id:
        flash('You are not authorized to access this interview', 'danger')
        return redirect(url_for('interview'))
    
    qa_pairs = InterviewQA.query.filter_by(interview_id=interview.id).all()
    
    # Set the current interview session
    session['interview_id'] = interview.id
    if 'current_question_index' not in session:
        session['current_question_index'] = 0
    
    return render_template('interview.html', 
                          interview=interview, 
                          qa_pairs=qa_pairs, 
                          current_index=session.get('current_question_index', 0))

@app.route('/interview/answer', methods=['POST'])
@login_required
def submit_answer():
    interview_id = session.get('interview_id')
    question_index = session.get('current_question_index', 0)
    
    if not interview_id:
        return jsonify({'error': 'No active interview session'}), 400
    
    interview = Interview.query.get_or_404(interview_id)
    
    if interview.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get the answer from the request
    answer = request.form.get('answer')
    qa_pairs = InterviewQA.query.filter_by(interview_id=interview_id).all()
    
    if question_index >= len(qa_pairs):
        return jsonify({'error': 'Question index out of range'}), 400
    
    qa_pair = qa_pairs[question_index]
    qa_pair.answer = answer
    
    # Analyze the answer and provide feedback
    feedback, score = analyze_answer(qa_pair.question, answer)
    qa_pair.feedback = feedback
    qa_pair.score = score
    
    db.session.commit()
    
    # Move to the next question
    session['current_question_index'] = question_index + 1
    
    # Check if this was the last question
    is_last = question_index + 1 >= len(qa_pairs)
    
    return jsonify({
        'feedback': feedback,
        'score': score,
        'nextIndex': session['current_question_index'],
        'isLast': is_last
    })

@app.route('/interview/speech-to-text', methods=['POST'])
@login_required
def process_speech():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if not audio_file:
        return jsonify({'error': 'Empty audio file provided'}), 400
    
    # Process the audio file to convert speech to text
    try:
        text = speech_to_text(audio_file)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/interview/text-to-speech', methods=['POST'])
@login_required
def get_speech():
    text = request.form.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        audio_data = text_to_speech(text)
        return audio_data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/interview/delete/<int:id>')
@login_required
def delete_interview(id):
    interview = Interview.query.get_or_404(id)
    
    if interview.user_id != current_user.id:
        flash('You are not authorized to delete this interview', 'danger')
        return redirect(url_for('interview'))
    
    # Delete all QA pairs associated with this interview
    InterviewQA.query.filter_by(interview_id=interview.id).delete()
    
    # Delete the interview itself
    db.session.delete(interview)
    db.session.commit()
    
    flash('Interview deleted successfully', 'success')
    return redirect(url_for('interview'))

# Opportunities routes
@app.route('/opportunities')
@login_required
def opportunities():
    saved_jobs = SavedJob.query.filter_by(user_id=current_user.id).all()
    saved_hackathons = SavedHackathon.query.filter_by(user_id=current_user.id).all()
    
    return render_template('opportunities.html', 
                          saved_jobs=saved_jobs,
                          saved_hackathons=saved_hackathons)

@app.route('/opportunities/search-jobs', methods=['POST'])
@login_required
def search_jobs_route():
    query = request.form.get('query')
    job_type = request.form.get('job_type')
    location = request.form.get('location')
    
    results = search_jobs(query, job_type, location)
    
    return jsonify(results)

@app.route('/opportunities/search-hackathons', methods=['POST'])
@login_required
def search_hackathons_route():
    query = request.form.get('query')
    beginner_friendly = True if request.form.get('beginner_friendly') else False
    team_based = True if request.form.get('team_based') else False
    sponsored = True if request.form.get('sponsored') else False
    
    results = search_hackathons(query, beginner_friendly, team_based, sponsored)
    
    return jsonify(results)

@app.route('/opportunities/save-job', methods=['POST'])
@login_required
def save_job():
    title = request.form.get('title')
    company = request.form.get('company')
    location = request.form.get('location')
    job_type = request.form.get('job_type')
    url = request.form.get('url')
    description = request.form.get('description')
    deadline_str = request.form.get('deadline')
    
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
    
    job = SavedJob(
        user_id=current_user.id,
        title=title,
        company=company,
        location=location,
        job_type=job_type,
        url=url,
        description=description,
        deadline=deadline,
        applied=False,
        notes=""
    )
    
    db.session.add(job)
    db.session.commit()
    
    flash('Job saved successfully', 'success')
    return redirect(url_for('opportunities'))

@app.route('/opportunities/save-hackathon', methods=['POST'])
@login_required
def save_hackathon():
    name = request.form.get('name')
    organizer = request.form.get('organizer')
    location = request.form.get('location')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    url = request.form.get('url')
    description = request.form.get('description')
    is_beginner_friendly = True if request.form.get('is_beginner_friendly') else False
    is_team_based = True if request.form.get('is_team_based') else False
    is_sponsored = True if request.form.get('is_sponsored') else False
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    hackathon = SavedHackathon(
        user_id=current_user.id,
        name=name,
        organizer=organizer,
        location=location,
        start_date=start_date,
        end_date=end_date,
        url=url,
        description=description,
        is_beginner_friendly=is_beginner_friendly,
        is_team_based=is_team_based,
        is_sponsored=is_sponsored,
        registered=False,
        notes=""
    )
    
    db.session.add(hackathon)
    db.session.commit()
    
    flash('Hackathon saved successfully', 'success')
    return redirect(url_for('opportunities'))

@app.route('/opportunities/update-job/<int:id>', methods=['POST'])
@login_required
def update_job(id):
    job = SavedJob.query.get_or_404(id)
    
    if job.user_id != current_user.id:
        flash('You are not authorized to update this job', 'danger')
        return redirect(url_for('opportunities'))
    
    job.applied = True if request.form.get('applied') else False
    job.notes = request.form.get('notes')
    
    db.session.commit()
    
    flash('Job updated successfully', 'success')
    return redirect(url_for('opportunities'))

@app.route('/opportunities/update-hackathon/<int:id>', methods=['POST'])
@login_required
def update_hackathon(id):
    hackathon = SavedHackathon.query.get_or_404(id)
    
    if hackathon.user_id != current_user.id:
        flash('You are not authorized to update this hackathon', 'danger')
        return redirect(url_for('opportunities'))
    
    hackathon.registered = True if request.form.get('registered') else False
    hackathon.notes = request.form.get('notes')
    
    db.session.commit()
    
    flash('Hackathon updated successfully', 'success')
    return redirect(url_for('opportunities'))

@app.route('/opportunities/delete-job/<int:id>')
@login_required
def delete_job(id):
    job = SavedJob.query.get_or_404(id)
    
    if job.user_id != current_user.id:
        flash('You are not authorized to delete this job', 'danger')
        return redirect(url_for('opportunities'))
    
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully', 'success')
    return redirect(url_for('opportunities'))

@app.route('/opportunities/delete-hackathon/<int:id>')
@login_required
def delete_hackathon(id):
    hackathon = SavedHackathon.query.get_or_404(id)
    
    if hackathon.user_id != current_user.id:
        flash('You are not authorized to delete this hackathon', 'danger')
        return redirect(url_for('opportunities'))
    
    db.session.delete(hackathon)
    db.session.commit()
    
    flash('Hackathon deleted successfully', 'success')
    return redirect(url_for('opportunities'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Get counts
    resume_count = Resume.query.filter_by(user_id=current_user.id).count()
    interview_count = Interview.query.filter_by(user_id=current_user.id).count()
    job_count = SavedJob.query.filter_by(user_id=current_user.id).count()
    hackathon_count = SavedHackathon.query.filter_by(user_id=current_user.id).count()
    
    # Get latest items
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    latest_interview = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.created_at.desc()).first()
    
    # Get upcoming deadlines
    upcoming_jobs = SavedJob.query.filter_by(user_id=current_user.id, applied=False)\
        .filter(SavedJob.deadline != None)\
        .order_by(SavedJob.deadline).limit(5).all()
        
    upcoming_hackathons = SavedHackathon.query.filter_by(user_id=current_user.id, registered=False)\
        .filter(SavedHackathon.start_date != None)\
        .order_by(SavedHackathon.start_date).limit(5).all()
    
    # Get skills distribution
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    skill_categories = {}
    for skill in skills:
        category = skill.category or 'Uncategorized'
        if category in skill_categories:
            skill_categories[category] += 1
        else:
            skill_categories[category] = 1
    
    return render_template('dashboard.html',
                          resume_count=resume_count,
                          interview_count=interview_count,
                          job_count=job_count,
                          hackathon_count=hackathon_count,
                          latest_resume=latest_resume,
                          latest_interview=latest_interview,
                          upcoming_jobs=upcoming_jobs,
                          upcoming_hackathons=upcoming_hackathons,
                          skill_categories=skill_categories)
