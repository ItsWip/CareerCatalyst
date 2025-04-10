from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_required, current_user
from io import BytesIO
from models import Resume
from utils.resume_generator import generate_customized_resume, render_resume_html, generate_resume_pdf
from utils.nlp_utils import extract_keywords, suggest_resume_improvements

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/')
@login_required
def index():
    """List all user resumes"""
    resumes = current_app.resumes.get(current_user.username, [])
    return render_template('resume/generator.html', resumes=resumes)

@resume_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Generate a new resume based on job description"""
    profile = current_app.profiles.get(current_user.username)
    
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile.edit'))
    
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        template = request.form.get('template', 'professional')
        
        if not job_title or not job_description:
            flash('Job title and description are required.', 'danger')
            return redirect(url_for('resume.generate'))
        
        # Generate customized resume
        resume_data = generate_customized_resume(
            profile.__dict__,
            job_title,
            job_description,
            template
        )
        
        if not resume_data:
            flash('Failed to generate resume. Please try again.', 'danger')
            return redirect(url_for('resume.generate'))
        
        # Create Resume object
        resume = Resume(
            user_id=current_user.username,
            job_title=job_title,
            job_description=job_description,
            template=template
        )
        
        resume.keywords = resume_data['keywords']
        resume.sections = resume_data
        resume.score = resume_data['match_score']
        
        # Save resume to in-memory storage
        if current_user.username not in current_app.resumes:
            current_app.resumes[current_user.username] = []
        
        current_app.resumes[current_user.username].append(resume)
        
        flash('Resume generated successfully.', 'success')
        return redirect(url_for('resume.preview', index=len(current_app.resumes[current_user.username]) - 1))
    
    return render_template('resume/generator.html')

@resume_bp.route('/preview/<int:index>')
@login_required
def preview(index):
    """Preview a specific resume"""
    resumes = current_app.resumes.get(current_user.username, [])
    
    if index >= len(resumes):
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.index'))
    
    resume = resumes[index]
    
    # Get improvement suggestions
    profile = current_app.profiles.get(current_user.username)
    profile_text = ""
    
    if profile:
        profile_text = profile.personal_info.get('summary', '') + " "
        profile_text += " ".join(profile.skills) + " "
        
        for exp in profile.experience:
            profile_text += exp.title + " " + exp.description + " "
        
        for proj in profile.projects:
            profile_text += proj.name + " " + proj.description + " "
            profile_text += " ".join(proj.technologies) + " "
    
    suggestions = suggest_resume_improvements(profile_text, resume.job_description)
    
    return render_template('resume/preview.html', resume=resume, index=index, suggestions=suggestions)

@resume_bp.route('/download/<int:index>')
@login_required
def download(index):
    """Download resume as PDF"""
    resumes = current_app.resumes.get(current_user.username, [])
    
    if index >= len(resumes):
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.index'))
    
    resume = resumes[index]
    
    # Render HTML
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('resume.index'))
    
    html_content = render_resume_html(resume.sections, resume.template)
    
    # Generate PDF
    pdf_data = generate_resume_pdf(html_content)
    
    if not pdf_data:
        flash('Failed to generate PDF. Please try again.', 'danger')
        return redirect(url_for('resume.preview', index=index))
    
    # Send file to user
    return send_file(
        BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{profile.personal_info.get('full_name', 'Resume')}_{resume.job_title}.pdf"
    )

@resume_bp.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete(index):
    """Delete a resume"""
    resumes = current_app.resumes.get(current_user.username, [])
    
    if index >= len(resumes):
        return jsonify({'success': False, 'message': 'Resume not found.'})
    
    try:
        del resumes[index]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@resume_bp.route('/analyze-job', methods=['POST'])
@login_required
def analyze_job():
    """Analyze job description and extract keywords"""
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        return jsonify({'success': False, 'message': 'Job description is required.'})
    
    # Extract keywords
    keywords = extract_keywords(job_description)
    
    # Get profile data
    profile = current_app.profiles.get(current_user.username)
    profile_text = ""
    
    if profile:
        profile_text = profile.personal_info.get('summary', '') + " "
        profile_text += " ".join(profile.skills) + " "
        
        for exp in profile.experience:
            profile_text += exp.title + " " + exp.description + " "
        
        for proj in profile.projects:
            profile_text += proj.name + " " + proj.description + " "
            profile_text += " ".join(proj.technologies) + " "
    
    # Get suggestions
    suggestions = suggest_resume_improvements(profile_text, job_description)
    
    return jsonify({
        'success': True,
        'keywords': keywords,
        'suggestions': suggestions
    })
