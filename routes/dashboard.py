from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from utils.opportunity_finder import OpportunityFinder

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard home page"""
    # Get user profile
    profile = current_app.profiles.get(current_user.username)
    if not profile:
        # Should never happen, but just in case
        from models import Profile
        profile = Profile(current_user.username)
        current_app.profiles[current_user.username] = profile
    
    # Get user's resumes
    resumes = current_app.resumes.get(current_user.username, [])
    
    # Get user's interviews
    interviews = current_app.interviews.get(current_user.username, [])
    
    # Get saved opportunities
    saved_opportunities = current_app.saved_opportunities.get(current_user.username, [])
    
    # Get upcoming deadlines
    upcoming_deadlines = []
    
    # Add hackathons with upcoming deadlines
    for opp in saved_opportunities:
        if hasattr(opp, 'start_date') and opp.start_date:
            # Only include if within the next 14 days
            if datetime.now() <= opp.start_date <= datetime.now() + timedelta(days=14):
                upcoming_deadlines.append({
                    'type': 'hackathon',
                    'name': opp.name,
                    'date': opp.start_date,
                    'url': opp.url
                })
    
    # Sort deadlines by date
    upcoming_deadlines.sort(key=lambda x: x['date'])
    
    # Get personalized recommendations if profile is complete
    recommendations = None
    if profile.skills and profile.experience:
        finder = OpportunityFinder()
        recommendations = finder.get_personalized_recommendations(profile, limit=3)
    
    # Calculate profile completeness
    completeness = calculate_profile_completeness(profile)
    
    # Calculate interview performance
    interview_stats = calculate_interview_stats(interviews)
    
    # Get recent activity
    recent_activity = get_recent_activity(profile, resumes, interviews, saved_opportunities)
    
    return render_template(
        'dashboard.html',
        profile=profile,
        resumes=resumes,
        interviews=interviews,
        saved_opportunities=saved_opportunities,
        upcoming_deadlines=upcoming_deadlines,
        recommendations=recommendations,
        completeness=completeness,
        interview_stats=interview_stats,
        recent_activity=recent_activity
    )

def calculate_profile_completeness(profile):
    """Calculate profile completeness percentage"""
    sections = [
        # Basic info
        bool(profile.personal_info.get('full_name')),
        bool(profile.personal_info.get('email')),
        bool(profile.personal_info.get('phone')),
        bool(profile.personal_info.get('location')),
        
        # Online presence
        bool(profile.personal_info.get('linkedin') or 
             profile.personal_info.get('github') or 
             profile.personal_info.get('website')),
        
        # Summary
        bool(profile.personal_info.get('summary')),
        
        # Skills, Education, Experience, Projects
        bool(profile.skills),
        bool(profile.education),
        bool(profile.experience),
        bool(profile.projects)
    ]
    
    completed = sum(1 for section in sections if section)
    return (completed / len(sections)) * 100

def calculate_interview_stats(interviews):
    """Calculate interview statistics"""
    if not interviews:
        return {
            'total': 0,
            'average_score': 0,
            'highest_score': 0,
            'completed_questions': 0,
            'recent_scores': []
        }
    
    scores = [interview.score for interview in interviews if hasattr(interview, 'score')]
    
    # Count total questions completed
    completed_questions = 0
    for interview in interviews:
        if hasattr(interview, 'questions'):
            completed_questions += sum(1 for q in interview.questions if hasattr(q, 'answer') and q.answer)
    
    # Get recent scores (last 5)
    recent_scores = scores[-5:] if scores else []
    
    return {
        'total': len(interviews),
        'average_score': sum(scores) / len(scores) if scores else 0,
        'highest_score': max(scores) if scores else 0,
        'completed_questions': completed_questions,
        'recent_scores': recent_scores
    }

def get_recent_activity(profile, resumes, interviews, saved_opportunities):
    """Get recent user activity"""
    activities = []
    
    # Profile updates
    if hasattr(profile, 'last_updated'):
        activities.append({
            'type': 'profile_update',
            'date': profile.last_updated,
            'description': 'Updated your profile'
        })
    
    # Resume generation
    for resume in resumes:
        if hasattr(resume, 'created_at'):
            activities.append({
                'type': 'resume_created',
                'date': resume.created_at,
                'description': f'Created resume for "{resume.job_title}"'
            })
    
    # Interview practice
    for interview in interviews:
        if hasattr(interview, 'date'):
            activities.append({
                'type': 'interview_practice',
                'date': interview.date,
                'description': f'Practiced {interview.role} interview'
            })
    
    # Saved opportunities
    for opp in saved_opportunities:
        if hasattr(opp, 'saved_date'):
            if hasattr(opp, 'job_type'):
                activities.append({
                    'type': 'saved_job',
                    'date': opp.saved_date,
                    'description': f'Saved job: {opp.title} at {opp.company}'
                })
            else:
                activities.append({
                    'type': 'saved_hackathon',
                    'date': opp.saved_date,
                    'description': f'Saved hackathon: {opp.name}'
                })
    
    # Sort by date (newest first)
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Return the 10 most recent activities
    return activities[:10]
