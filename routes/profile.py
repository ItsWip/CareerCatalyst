from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import Education, WorkExperience, Project, Certification

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
@login_required
def view():
    """View user profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('profile/view.html', profile=profile)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Update personal info
        profile.personal_info = {
            'full_name': request.form.get('full_name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'location': request.form.get('location', ''),
            'linkedin': request.form.get('linkedin', ''),
            'github': request.form.get('github', ''),
            'website': request.form.get('website', ''),
            'summary': request.form.get('summary', '')
        }
        
        # Update skills
        profile.skills = [s.strip() for s in request.form.get('skills', '').split(',') if s.strip()]
        
        profile.last_updated = datetime.now()
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.view'))
    
    return render_template('profile/edit.html', profile=profile)

@profile_bp.route('/education/add', methods=['POST'])
@login_required
def add_education():
    """Add education to profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found.'})
    
    try:
        education = Education(
            degree=request.form.get('degree', ''),
            institution=request.form.get('institution', ''),
            location=request.form.get('location', ''),
            start_date=request.form.get('start_date', ''),
            end_date=request.form.get('end_date', ''),
            gpa=request.form.get('gpa', ''),
            description=request.form.get('description', '')
        )
        
        profile.education.append(education)
        profile.last_updated = datetime.now()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/education/remove/<int:index>', methods=['POST'])
@login_required
def remove_education(index):
    """Remove education from profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile or index >= len(profile.education):
        return jsonify({'success': False, 'message': 'Education not found.'})
    
    try:
        del profile.education[index]
        profile.last_updated = datetime.now()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/experience/add', methods=['POST'])
@login_required
def add_experience():
    """Add work experience to profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found.'})
    
    try:
        # Parse responsibilities and achievements
        responsibilities = request.form.get('responsibilities', '').split('\n')
        responsibilities = [r.strip() for r in responsibilities if r.strip()]
        
        achievements = request.form.get('achievements', '').split('\n')
        achievements = [a.strip() for a in achievements if a.strip()]
        
        experience = WorkExperience(
            title=request.form.get('title', ''),
            company=request.form.get('company', ''),
            location=request.form.get('location', ''),
            start_date=request.form.get('start_date', ''),
            end_date=request.form.get('end_date', ''),
            description=request.form.get('description', ''),
            responsibilities=responsibilities,
            achievements=achievements
        )
        
        profile.experience.append(experience)
        profile.last_updated = datetime.now()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/experience/remove/<int:index>', methods=['POST'])
@login_required
def remove_experience(index):
    """Remove work experience from profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile or index >= len(profile.experience):
        return jsonify({'success': False, 'message': 'Experience not found.'})
    
    try:
        del profile.experience[index]
        profile.last_updated = datetime.now()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/project/add', methods=['POST'])
@login_required
def add_project():
    """Add project to profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found.'})
    
    try:
        # Parse technologies
        technologies = request.form.get('technologies', '').split(',')
        technologies = [t.strip() for t in technologies if t.strip()]
        
        project = Project(
            name=request.form.get('name', ''),
            description=request.form.get('description', ''),
            technologies=technologies,
            url=request.form.get('url', ''),
            start_date=request.form.get('start_date', ''),
            end_date=request.form.get('end_date', '')
        )
        
        profile.projects.append(project)
        profile.last_updated = datetime.now()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/project/remove/<int:index>', methods=['POST'])
@login_required
def remove_project(index):
    """Remove project from profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile or index >= len(profile.projects):
        return jsonify({'success': False, 'message': 'Project not found.'})
    
    try:
        del profile.projects[index]
        profile.last_updated = datetime.now()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/certification/add', methods=['POST'])
@login_required
def add_certification():
    """Add certification to profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found.'})
    
    try:
        certification = Certification(
            name=request.form.get('name', ''),
            issuer=request.form.get('issuer', ''),
            date=request.form.get('date', ''),
            expiry=request.form.get('expiry', ''),
            url=request.form.get('url', '')
        )
        
        profile.certifications.append(certification)
        profile.last_updated = datetime.now()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/certification/remove/<int:index>', methods=['POST'])
@login_required
def remove_certification(index):
    """Remove certification from profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile or index >= len(profile.certifications):
        return jsonify({'success': False, 'message': 'Certification not found.'})
    
    try:
        del profile.certifications[index]
        profile.last_updated = datetime.now()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/achievement/add', methods=['POST'])
@login_required
def add_achievement():
    """Add achievement to profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found.'})
    
    try:
        achievement = request.form.get('achievement', '')
        if achievement:
            profile.achievements.append(achievement)
            profile.last_updated = datetime.now()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@profile_bp.route('/achievement/remove/<int:index>', methods=['POST'])
@login_required
def remove_achievement(index):
    """Remove achievement from profile"""
    profile = current_app.profiles.get(current_user.username)
    if not profile or index >= len(profile.achievements):
        return jsonify({'success': False, 'message': 'Achievement not found.'})
    
    try:
        del profile.achievements[index]
        profile.last_updated = datetime.now()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
