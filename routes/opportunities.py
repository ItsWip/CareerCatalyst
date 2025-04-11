from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from utils.opportunity_finder import OpportunityFinder

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/')
@login_required
def index():
    """Opportunities home page"""
    return redirect(url_for('opportunities.jobs'))

@opportunities_bp.route('/jobs')
@login_required
def jobs():
    """Job search page"""
    finder = OpportunityFinder()
    
    # Get filter parameters
    keywords = request.args.get('keywords', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    # Parse keywords
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()] if keywords else None
    
    # Check if we should use profile for recommendations
    use_profile = request.args.get('use_profile') == '1'
    profile = current_app.profiles.get(current_user.username) if use_profile else None
    
    # Search jobs
    job_results = finder.search_jobs(
        keywords=keyword_list,
        job_type=job_type if job_type else None,
        location=location if location else None,
        profile=profile
    )
    
    # Get saved opportunities
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    saved_job_urls = [opp.url for opp in saved_opportunities if hasattr(opp, 'job_type')]
    
    return render_template(
        'opportunities/jobs.html',
        jobs=job_results,
        keywords=keywords,
        job_type=job_type,
        location=location,
        use_profile=use_profile,
        saved_job_urls=saved_job_urls
    )

@opportunities_bp.route('/hackathons')
@login_required
def hackathons():
    """Hackathon search page"""
    finder = OpportunityFinder()
    
    # Get filter parameters
    keywords = request.args.get('keywords', '')
    location = request.args.get('location', '')
    remote = request.args.get('remote')
    skill_level = request.args.get('skill_level', '')
    team_size = request.args.get('team_size', '')
    
    # Parse keywords and remote filter
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()] if keywords else None
    remote_filter = None
    if remote == '1':
        remote_filter = True
    elif remote == '0':
        remote_filter = False
    
    # Search hackathons
    hackathon_results = finder.search_hackathons(
        keywords=keyword_list,
        location=location if location else None,
        remote=remote_filter,
        skill_level=skill_level if skill_level else None,
        team_size=team_size if team_size else None
    )
    
    # Get saved opportunities
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    saved_hackathon_urls = [opp.url for opp in saved_opportunities if hasattr(opp, 'is_remote')]
    
    return render_template(
        'opportunities/hackathons.html',
        hackathons=hackathon_results,
        keywords=keywords,
        location=location,
        remote=remote,
        skill_level=skill_level,
        team_size=team_size,
        saved_hackathon_urls=saved_hackathon_urls
    )

@opportunities_bp.route('/save-job', methods=['POST'])
@login_required
def save_job():
    """Save a job opportunity"""
    finder = OpportunityFinder()
    
    job_id = request.form.get('job_id')
    if not job_id or not job_id.isdigit():
        return jsonify({'success': False, 'message': 'Invalid job ID.'})
    
    job_id = int(job_id)
    
    if job_id < 0 or job_id >= len(finder.mock_jobs):
        return jsonify({'success': False, 'message': 'Job not found.'})
    
    job = finder.mock_jobs[job_id]
    
    # Check if already saved
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    if any(opp.url == job.url for opp in saved_opportunities):
        return jsonify({'success': False, 'message': 'Job already saved.'})
    
    # Save the job
    if current_user.username not in current_app.saved_opportunities:
        current_app.saved_opportunities[current_user.username] = []
    
    current_app.saved_opportunities[current_user.username].append(job)
    
    return jsonify({'success': True})

@opportunities_bp.route('/save-hackathon', methods=['POST'])
@login_required
def save_hackathon():
    """Save a hackathon opportunity"""
    finder = OpportunityFinder()
    
    hackathon_id = request.form.get('hackathon_id')
    if not hackathon_id or not hackathon_id.isdigit():
        return jsonify({'success': False, 'message': 'Invalid hackathon ID.'})
    
    hackathon_id = int(hackathon_id)
    
    if hackathon_id < 0 or hackathon_id >= len(finder.mock_hackathons):
        return jsonify({'success': False, 'message': 'Hackathon not found.'})
    
    hackathon = finder.mock_hackathons[hackathon_id]
    
    # Check if already saved
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    if any(opp.url == hackathon.url for opp in saved_opportunities):
        return jsonify({'success': False, 'message': 'Hackathon already saved.'})
    
    # Save the hackathon
    if current_user.username not in current_app.saved_opportunities:
        current_app.saved_opportunities[current_user.username] = []
    
    current_app.saved_opportunities[current_user.username].append(hackathon)
    
    return jsonify({'success': True})

@opportunities_bp.route('/remove-saved', methods=['POST'])
@login_required
def remove_saved():
    """Remove a saved opportunity"""
    url = request.form.get('url')
    if not url:
        return jsonify({'success': False, 'message': 'URL is required.'})
    
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    
    # Find and remove the opportunity
    for i, opp in enumerate(saved_opportunities):
        if opp.url == url:
            del saved_opportunities[i]
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Saved opportunity not found.'})

@opportunities_bp.route('/recommendations')
@login_required
def recommendations():
    """Get personalized recommendations"""
    profile = current_app.profiles.get(current_user.username)
    
    if not profile:
        flash('Please complete your profile to get personalized recommendations.', 'warning')
        return redirect(url_for('profile.edit'))
    
    # Get recommendations
    finder = OpportunityFinder()
    recommendations = finder.get_personalized_recommendations(profile)
    
    # Get saved opportunities
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    saved_urls = [opp.url for opp in saved_opportunities]
    
    return render_template(
        'opportunities/jobs.html',
        recommendations=recommendations,
        saved_urls=saved_urls,
        is_recommendation_page=True
    )
