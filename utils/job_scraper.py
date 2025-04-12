import requests
import json
import os
import random
from datetime import datetime, timedelta

# Sample job data for fallback mode
SAMPLE_JOBS = [
    {
        "title": "Software Engineer",
        "company": "Tech Innovators Inc.",
        "location": "San Francisco, CA",
        "description": "We're looking for a Software Engineer to join our team. You'll work on developing scalable web applications using modern technologies.",
        "requirements": "- 3+ years of experience in web development\n- Proficiency in Python, JavaScript\n- Experience with Flask, React\n- Strong problem-solving skills",
        "salary_range": "$120,000 - $150,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/software-engineer"
    },
    {
        "title": "Data Scientist",
        "company": "Data Metrics Solutions",
        "location": "Remote",
        "description": "Join our data science team to develop machine learning models and analyze large datasets to drive business decisions.",
        "requirements": "- Master's degree in Data Science, Statistics or related field\n- Experience with Python, R\n- Knowledge of machine learning algorithms\n- Familiarity with data visualization tools",
        "salary_range": "$115,000 - $140,000",
        "job_type": "Remote",
        "url": "https://example.com/jobs/data-scientist"
    },
    {
        "title": "UX/UI Designer",
        "company": "Creative Interfaces",
        "location": "New York, NY",
        "description": "Design intuitive and engaging user experiences for web and mobile applications.",
        "requirements": "- 2+ years in UX/UI design\n- Proficiency in design tools like Figma, Sketch\n- Portfolio demonstrating UX process\n- Understanding of user-centered design principles",
        "salary_range": "$90,000 - $115,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/ux-ui-designer"
    },
    {
        "title": "DevOps Engineer",
        "company": "Cloud Solutions Pro",
        "location": "Austin, TX",
        "description": "Implement and manage CI/CD pipelines, infrastructure as code, and cloud services.",
        "requirements": "- Experience with AWS/Azure/GCP\n- Knowledge of Docker, Kubernetes\n- Scripting in Python, Bash\n- Understanding of security best practices",
        "salary_range": "$125,000 - $160,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/devops-engineer"
    },
    {
        "title": "Product Manager",
        "company": "Innovative Products Inc.",
        "location": "Seattle, WA",
        "description": "Lead product development from conception to launch, working closely with cross-functional teams.",
        "requirements": "- 3+ years in product management\n- Strong analytical skills\n- Experience with agile methodologies\n- Excellent communication skills",
        "salary_range": "$130,000 - $160,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/product-manager"
    },
    {
        "title": "Frontend Developer",
        "company": "Web Experts",
        "location": "Remote",
        "description": "Build responsive web applications using modern JavaScript frameworks.",
        "requirements": "- Proficiency in JavaScript, HTML, CSS\n- Experience with React, Vue, or Angular\n- Understanding of web performance optimization\n- Knowledge of responsive design principles",
        "salary_range": "$95,000 - $120,000",
        "job_type": "Remote",
        "url": "https://example.com/jobs/frontend-developer"
    },
    {
        "title": "Backend Developer",
        "company": "Server Solutions",
        "location": "Chicago, IL",
        "description": "Develop robust backend services and APIs for web and mobile applications.",
        "requirements": "- Experience with server-side languages (Python, Node.js, Java)\n- Knowledge of database systems (SQL, NoSQL)\n- Understanding of RESTful API design\n- Familiarity with cloud services",
        "salary_range": "$100,000 - $130,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/backend-developer"
    },
    {
        "title": "Mobile Developer",
        "company": "App Innovations",
        "location": "Los Angeles, CA",
        "description": "Create native mobile applications for iOS and Android platforms.",
        "requirements": "- Experience with Swift/Kotlin or React Native\n- Understanding of mobile UI/UX principles\n- Knowledge of app store publishing processes\n- Familiarity with mobile design patterns",
        "salary_range": "$105,000 - $135,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/mobile-developer"
    },
    {
        "title": "Data Engineer",
        "company": "Data Pipeline Inc.",
        "location": "Remote",
        "description": "Design and implement data pipelines to collect, process, and store large-scale datasets.",
        "requirements": "- Experience with data processing frameworks (Spark, Hadoop)\n- Knowledge of SQL and NoSQL databases\n- Programming skills in Python, Scala\n- Understanding of data modeling concepts",
        "salary_range": "$115,000 - $145,000",
        "job_type": "Remote",
        "url": "https://example.com/jobs/data-engineer"
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Solutions",
        "location": "Boston, MA",
        "description": "Develop and deploy machine learning models to solve complex business problems.",
        "requirements": "- Advanced degree in Computer Science, AI, or related field\n- Experience with TensorFlow, PyTorch\n- Strong programming skills in Python\n- Understanding of ML deployment workflows",
        "salary_range": "$130,000 - $170,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/ml-engineer"
    },
    {
        "title": "QA Engineer",
        "company": "Quality First",
        "location": "Denver, CO",
        "description": "Ensure software quality through manual and automated testing processes.",
        "requirements": "- Experience with test automation frameworks\n- Knowledge of testing methodologies\n- Understanding of CI/CD pipelines\n- Attention to detail",
        "salary_range": "$85,000 - $110,000",
        "job_type": "Full-time",
        "url": "https://example.com/jobs/qa-engineer"
    },
    {
        "title": "Technical Writer",
        "company": "Documentation Pro",
        "location": "Remote",
        "description": "Create clear and comprehensive technical documentation for software products.",
        "requirements": "- Strong writing and editing skills\n- Ability to explain complex concepts clearly\n- Familiarity with documentation tools\n- Basic understanding of software development",
        "salary_range": "$75,000 - $95,000",
        "job_type": "Remote",
        "url": "https://example.com/jobs/technical-writer"
    }
]

# Sample hackathon data for fallback mode
SAMPLE_HACKATHONS = [
    {
        "name": "Code for Good",
        "organizer": "Tech for Change",
        "location": "San Francisco, CA",
        "description": "A weekend hackathon focused on building solutions for nonprofits and social enterprises.",
        "start_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/code-for-good",
        "is_beginner_friendly": True,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "AI Innovation Challenge",
        "organizer": "AI Research Institute",
        "location": "Online",
        "description": "Develop innovative AI solutions to real-world problems in healthcare, education, or sustainability.",
        "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/ai-innovation",
        "is_beginner_friendly": False,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "Startup Weekend",
        "organizer": "Entrepreneurship Network",
        "location": "New York, NY",
        "description": "Launch a startup in just 54 hours, from idea to pitch.",
        "start_date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=47)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/startup-weekend",
        "is_beginner_friendly": True,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "Cybersecurity Hack Days",
        "organizer": "Security Alliance",
        "location": "Washington, DC",
        "description": "Find and fix security vulnerabilities in open-source software.",
        "start_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=61)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/cybersecurity",
        "is_beginner_friendly": False,
        "is_team_based": True,
        "is_sponsored": False
    },
    {
        "name": "Health Tech Hackathon",
        "organizer": "Medical Innovations",
        "location": "Boston, MA",
        "description": "Create innovative solutions to improve healthcare delivery and patient outcomes.",
        "start_date": (datetime.now() + timedelta(days=75)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=76)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/health-tech",
        "is_beginner_friendly": True,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "Climate Action Hackathon",
        "organizer": "Sustainable Future",
        "location": "Online",
        "description": "Build technology solutions to address climate change and environmental challenges.",
        "start_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/climate-action",
        "is_beginner_friendly": True,
        "is_team_based": False,
        "is_sponsored": False
    },
    {
        "name": "Fintech Innovation Challenge",
        "organizer": "Financial Technology Association",
        "location": "Chicago, IL",
        "description": "Develop innovative solutions for financial services and banking technology.",
        "start_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=91)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/fintech",
        "is_beginner_friendly": False,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "Blockchain Builder Fest",
        "organizer": "Crypto Community",
        "location": "Miami, FL",
        "description": "Create decentralized applications (dApps) on blockchain platforms.",
        "start_date": (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=42)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/blockchain",
        "is_beginner_friendly": False,
        "is_team_based": True,
        "is_sponsored": True
    },
    {
        "name": "Game Development Jam",
        "organizer": "Game Creators Guild",
        "location": "Los Angeles, CA",
        "description": "Design and develop innovative games in a weekend.",
        "start_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=27)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/game-jam",
        "is_beginner_friendly": True,
        "is_team_based": True,
        "is_sponsored": False
    },
    {
        "name": "Education Technology Hackathon",
        "organizer": "Learning Innovations",
        "location": "Online",
        "description": "Build tools and platforms to improve education delivery and accessibility.",
        "start_date": (datetime.now() + timedelta(days=55)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=56)).strftime("%Y-%m-%d"),
        "url": "https://example.com/hackathons/edtech",
        "is_beginner_friendly": True,
        "is_team_based": False,
        "is_sponsored": True
    }
]

def search_jobs(query=None, job_type=None, location=None):
    """
    Search for jobs using a job search API or fall back to sample data.
    
    Args:
        query (str): Search keywords
        job_type (str): Type of job (remote, full-time, part-time, internship)
        location (str): Job location
        
    Returns:
        list: Job listings matching the search criteria
    """
    # Try to use a real job search API if available
    api_key = os.environ.get("JOB_SEARCH_API_KEY")
    
    if api_key:
        try:
            # Implement actual API call here
            # For example, using the RapidAPI Jobs API
            url = "https://jsearch.p.rapidapi.com/search"
            
            # Prepare query parameters
            params = {
                "query": f"{query or ''} {job_type or ''} {location or ''}".strip(),
                "page": "1",
                "num_pages": "1"
            }
            
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process and format the response data
                jobs = []
                for job in data.get("data", []):
                    jobs.append({
                        "title": job.get("job_title"),
                        "company": job.get("employer_name"),
                        "location": job.get("job_city") + ", " + job.get("job_country") if job.get("job_city") else job.get("job_country"),
                        "description": job.get("job_description"),
                        "job_type": job.get("job_employment_type"),
                        "url": job.get("job_apply_link"),
                        "date_posted": job.get("job_posted_at_datetime_utc"),
                        "salary_range": job.get("job_salary_currency") + job.get("job_salary") if job.get("job_salary") else "Not specified"
                    })
                
                return jobs
            
        except Exception as e:
            print(f"Error accessing job search API: {e}")
    
    # Fall back to sample job data
    # Filter based on search parameters
    filtered_jobs = SAMPLE_JOBS.copy()
    
    if query:
        query = query.lower()
        filtered_jobs = [job for job in filtered_jobs if 
                        query in job["title"].lower() or 
                        query in job["company"].lower() or 
                        query in job["description"].lower() or 
                        (job.get("requirements") and query in job["requirements"].lower())]
    
    if job_type:
        job_type = job_type.lower()
        filtered_jobs = [job for job in filtered_jobs if 
                        job_type in job["job_type"].lower()]
    
    if location:
        location = location.lower()
        filtered_jobs = [job for job in filtered_jobs if 
                        location in job["location"].lower()]
    
    # Add a random deadline date within next 30 days
    for job in filtered_jobs:
        random_days = random.randint(7, 30)
        deadline = datetime.now() + timedelta(days=random_days)
        job["deadline"] = deadline.strftime("%Y-%m-%d")
    
    return filtered_jobs

def search_hackathons(query=None, beginner_friendly=False, team_based=False, sponsored=False):
    """
    Search for hackathons using an API or fall back to sample data.
    
    Args:
        query (str): Search keywords
        beginner_friendly (bool): Filter for beginner-friendly hackathons
        team_based (bool): Filter for team-based hackathons
        sponsored (bool): Filter for sponsored hackathons
        
    Returns:
        list: Hackathon listings matching the search criteria
    """
    # Try to use a real hackathon search API if available
    api_key = os.environ.get("HACKATHON_API_KEY")
    
    if api_key:
        try:
            # Implement actual API call here if one becomes available
            # Currently, there isn't a widely available hackathon API
            pass
            
        except Exception as e:
            print(f"Error accessing hackathon API: {e}")
    
    # Fall back to sample hackathon data
    # Filter based on search parameters
    filtered_hackathons = SAMPLE_HACKATHONS.copy()
    
    if query:
        query = query.lower()
        filtered_hackathons = [hackathon for hackathon in filtered_hackathons if 
                              query in hackathon["name"].lower() or 
                              query in hackathon["organizer"].lower() or 
                              query in hackathon["description"].lower() or
                              query in hackathon["location"].lower()]
    
    if beginner_friendly:
        filtered_hackathons = [hackathon for hackathon in filtered_hackathons if 
                              hackathon["is_beginner_friendly"]]
    
    if team_based:
        filtered_hackathons = [hackathon for hackathon in filtered_hackathons if 
                              hackathon["is_team_based"]]
    
    if sponsored:
        filtered_hackathons = [hackathon for hackathon in filtered_hackathons if 
                              hackathon["is_sponsored"]]
    
    return filtered_hackathons
