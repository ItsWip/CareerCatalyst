from datetime import datetime

class User:
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.last_login = datetime.now()
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return self.username

class Profile:
    def __init__(self, username):
        self.username = username
        self.personal_info = {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "website": "",
            "summary": ""
        }
        self.education = []  # List of Education objects
        self.experience = []  # List of WorkExperience objects
        self.projects = []  # List of Project objects
        self.skills = []  # List of strings
        self.certifications = []  # List of Certification objects
        self.achievements = []  # List of strings
        self.last_updated = datetime.now()

class Education:
    def __init__(self, degree, institution, location, start_date, end_date, gpa=None, description=None):
        self.degree = degree
        self.institution = institution
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.gpa = gpa
        self.description = description

class WorkExperience:
    def __init__(self, title, company, location, start_date, end_date, description, responsibilities=None, achievements=None):
        self.title = title
        self.company = company
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.responsibilities = responsibilities or []
        self.achievements = achievements or []

class Project:
    def __init__(self, name, description, technologies, url=None, start_date=None, end_date=None):
        self.name = name
        self.description = description
        self.technologies = technologies  # List of strings
        self.url = url
        self.start_date = start_date
        self.end_date = end_date

class Certification:
    def __init__(self, name, issuer, date, expiry=None, url=None):
        self.name = name
        self.issuer = issuer
        self.date = date
        self.expiry = expiry
        self.url = url

class Resume:
    def __init__(self, user_id, job_title, job_description, template="professional"):
        self.user_id = user_id
        self.job_title = job_title
        self.job_description = job_description
        self.template = template
        self.created_at = datetime.now()
        self.keywords = []  # Extracted keywords from job description
        self.sections = {}  # Customized content for the resume
        self.score = 0  # Matching score for this resume

class Interview:
    def __init__(self, user_id, role, mode="text"):
        self.user_id = user_id
        self.role = role
        self.mode = mode  # "text" or "audio"
        self.date = datetime.now()
        self.questions = []  # List of Question objects
        self.feedback = {}  # Overall feedback for the interview
        self.score = 0  # Overall interview score

class Question:
    def __init__(self, question_text, question_type):
        self.question_text = question_text
        self.question_type = question_type  # "technical", "behavioral", "hr"
        self.answer = None
        self.feedback = None
        self.score = 0  # Score for this particular question

class JobOpportunity:
    def __init__(self, title, company, location, job_type, description, url, posted_date):
        self.title = title
        self.company = company
        self.location = location
        self.job_type = job_type  # "remote", "full-time", "part-time", "internship"
        self.description = description
        self.url = url
        self.posted_date = posted_date
        self.saved_date = datetime.now()
        self.match_score = 0  # Match score with user profile

class Hackathon:
    def __init__(self, name, organizer, location, start_date, end_date, description, 
                 url, is_remote, skill_level, team_size, prizes=None):
        self.name = name
        self.organizer = organizer
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.url = url
        self.is_remote = is_remote
        self.skill_level = skill_level  # "beginner", "intermediate", "advanced"
        self.team_size = team_size  # "individual", "team", "both"
        self.prizes = prizes or []
        self.saved_date = datetime.now()
