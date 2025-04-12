import os
import logging
import tempfile
from datetime import datetime
from utils.nlp_utils import extract_keywords, calculate_match_score

def generate_customized_resume(profile, job_title, job_description, template_name="professional"):
    """
    Generate a customized resume based on the job description
    
    Args:
        profile (dict): User profile data
        job_title (str): Job title
        job_description (str): Job description
        template_name (str): Template name
        
    Returns:
        dict: Resume data
    """
    if not profile or not job_description:
        logging.error("Missing profile or job description")
        return None
    
    # Extract keywords from job description
    keywords = extract_keywords(job_description)
    
    # Create a flat string of the profile for matching
    profile_text = ""
    if profile.get('personal_info'):
        profile_text += profile['personal_info'].get('summary', '') + " "
    
    for skill in profile.get('skills', []):
        profile_text += skill + " "
    
    for exp in profile.get('experience', []):
        profile_text += exp.get('title', '') + " " + exp.get('description', '') + " "
        for resp in exp.get('responsibilities', []):
            profile_text += resp + " "
    
    for proj in profile.get('projects', []):
        profile_text += proj.get('name', '') + " " + proj.get('description', '') + " "
        for tech in proj.get('technologies', []):
            profile_text += tech + " "
    
    # Calculate match score
    match_score = calculate_match_score(profile_text, job_description)
    
    # Reorder skills based on keywords
    prioritized_skills = []
    other_skills = []
    
    for skill in profile.get('skills', []):
        if skill.lower() in [kw.lower() for kw in keywords]:
            prioritized_skills.append(skill)
        else:
            other_skills.append(skill)
    
    ordered_skills = prioritized_skills + other_skills
    
    # Reorder experience and projects based on relevance to keywords
    def calculate_relevance(item, keywords):
        text = item.get('title', '') + " " + item.get('description', '')
        matches = sum(1 for kw in keywords if kw.lower() in text.lower())
        return matches
    
    ordered_experience = sorted(
        profile.get('experience', []),
        key=lambda x: calculate_relevance(x, keywords),
        reverse=True
    )
    
    ordered_projects = sorted(
        profile.get('projects', []),
        key=lambda x: calculate_relevance(x, keywords),
        reverse=True
    )
    
    # Prepare resume data
    resume_data = {
        'created_at': datetime.now(),
        'template': template_name,
        'job_title': job_title,
        'match_score': match_score,
        'keywords': keywords,
        'personal_info': profile.get('personal_info', {}),
        'skills': ordered_skills,
        'experience': ordered_experience,
        'education': profile.get('education', []),
        'projects': ordered_projects,
        'certifications': profile.get('certifications', []),
        'achievements': profile.get('achievements', [])
    }
    
    return resume_data

def render_resume_html(resume_data, template_name="professional"):
    """
    Render resume HTML using a simple template
    
    Args:
        resume_data (dict): Resume data
        template_name (str): Template name
        
    Returns:
        str: Rendered HTML
    """
    if not resume_data:
        return "<p>No resume data provided</p>"
    
    try:
        # Simple HTML template string
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resume</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .resume-header { text-align: center; margin-bottom: 20px; }
                .section { margin-bottom: 20px; }
                .section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #ccc; }
                .skills-list { display: flex; flex-wrap: wrap; }
                .skill-item { background: #f0f0f0; padding: 5px 10px; margin: 5px; border-radius: 3px; }
                .item { margin-bottom: 15px; }
                .item-title { font-weight: bold; margin-bottom: 5px; }
                .item-subtitle { font-style: italic; margin-bottom: 5px; }
                .item-date { color: #666; font-size: 14px; }
                .item-description { margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="resume-header">
                <h1>{full_name}</h1>
                <div>{email} | {phone} | {location}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Summary</div>
                <p>{summary}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Skills</div>
                <div class="skills-list">
                    {skills}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Experience</div>
                {experience}
            </div>
            
            <div class="section">
                <div class="section-title">Education</div>
                {education}
            </div>
            
            <div class="section">
                <div class="section-title">Projects</div>
                {projects}
            </div>
        </body>
        </html>
        """
        
        # Format the HTML with resume data
        personal_info = resume_data.get('personal_info', {})
        
        # Format skills
        skills_html = ""
        for skill in resume_data.get('skills', []):
            skills_html += f'<div class="skill-item">{skill}</div>'
        
        # Format experience
        experience_html = ""
        for exp in resume_data.get('experience', []):
            experience_html += f"""
            <div class="item">
                <div class="item-title">{exp.get('title', '')}</div>
                <div class="item-subtitle">{exp.get('company', '')}, {exp.get('location', '')}</div>
                <div class="item-date">{exp.get('start_date', '')} - {exp.get('end_date', '')}</div>
                <div class="item-description">{exp.get('description', '')}</div>
            </div>
            """
        
        # Format education
        education_html = ""
        for edu in resume_data.get('education', []):
            education_html += f"""
            <div class="item">
                <div class="item-title">{edu.get('degree', '')}</div>
                <div class="item-subtitle">{edu.get('institution', '')}, {edu.get('location', '')}</div>
                <div class="item-date">{edu.get('start_date', '')} - {edu.get('end_date', '')}</div>
                <div class="item-description">GPA: {edu.get('gpa', 'N/A')}</div>
            </div>
            """
        
        # Format projects
        projects_html = ""
        for proj in resume_data.get('projects', []):
            projects_html += f"""
            <div class="item">
                <div class="item-title">{proj.get('name', '')}</div>
                <div class="item-description">{proj.get('description', '')}</div>
                <div class="item-description">Technologies: {', '.join(proj.get('technologies', []))}</div>
            </div>
            """
        
        # Substitute values into the template
        formatted_html = html.format(
            full_name=personal_info.get('full_name', 'Name'),
            email=personal_info.get('email', 'Email'),
            phone=personal_info.get('phone', 'Phone'),
            location=personal_info.get('location', 'Location'),
            summary=personal_info.get('summary', 'No summary provided'),
            skills=skills_html,
            experience=experience_html,
            education=education_html,
            projects=projects_html
        )
        
        return formatted_html
    
    except Exception as e:
        logging.error(f"Error rendering resume HTML: {str(e)}")
        return f"<p>Error generating resume: {str(e)}</p>"

def generate_resume_pdf(html_content):
    """
    Generate PDF from HTML content
    
    Args:
        html_content (str): HTML content
        
    Returns:
        bytes: HTML content as bytes for now, PDF functionality to be added later
    """
    logging.warning("PDF generation is temporarily disabled. Returning HTML content.")
    # For now we just return the HTML content encoded as bytes
    # Once the PDF generation dependencies are installed, this will be updated
    try:
        return html_content.encode('utf-8')
    except Exception as e:
        logging.error(f"Error preparing HTML content: {str(e)}")
        return None
