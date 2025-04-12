import logging
import random
import re
from datetime import datetime, timedelta
from utils.nlp_utils import extract_keywords, calculate_match_score

class OpportunityFinder:
    """Class to handle job and hackathon opportunity search and recommendations"""
    
    def __init__(self):
        # In real implementation, this would be connected to APIs or web scraping
        self.mock_jobs = self._generate_mock_jobs()
        self.mock_hackathons = self._generate_mock_hackathons()
    
    def search_jobs(self, keywords=None, job_type=None, location=None, profile=None):
        """
        Search for job opportunities
        
        Args:
            keywords (list): Keywords to search for
            job_type (str): Type of job ("remote", "full-time", "part-time", "internship")
            location (str): Job location
            profile (dict): User profile for matching
            
        Returns:
            list: Job opportunities
        """
        # In a real implementation, this would call external APIs or job boards
        # For MVP, we'll use the mock data with filtering
        
        filtered_jobs = self.mock_jobs
        
        # Filter by job type
        if job_type:
            filtered_jobs = [job for job in filtered_jobs if job.job_type == job_type]
        
        # Filter by location (simple substring match)
        if location:
            filtered_jobs = [job for job in filtered_jobs if location.lower() in job.location.lower()]
        
        # Filter by keywords
        if keywords:
            filtered_jobs = [
                job for job in filtered_jobs 
                if any(kw.lower() in job.title.lower() or kw.lower() in job.description.lower() 
                      for kw in keywords)
            ]
        
        # Calculate match score if profile provided
        if profile:
            profile_text = self._profile_to_text(profile)
            for job in filtered_jobs:
                job_text = f"{job.title} {job.description}"
                job.match_score = calculate_match_score(profile_text, job_text)
            
            # Sort by match score
            filtered_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        return filtered_jobs
    
    def search_hackathons(self, keywords=None, location=None, remote=None, skill_level=None, team_size=None):
        """
        Search for hackathon opportunities
        
        Args:
            keywords (list): Keywords to search for
            location (str): Hackathon location
            remote (bool): Whether hackathon is remote
            skill_level (str): Skill level ("beginner", "intermediate", "advanced")
            team_size (str): Team size ("individual", "team", "both")
            
        Returns:
            list: Hackathon opportunities
        """
        # In a real implementation, this would call external APIs or hackathon platforms
        # For MVP, we'll use the mock data with filtering
        
        filtered_hackathons = self.mock_hackathons
        
        # Filter by location
        if location:
            filtered_hackathons = [h for h in filtered_hackathons if location.lower() in h.location.lower()]
        
        # Filter by remote
        if remote is not None:
            filtered_hackathons = [h for h in filtered_hackathons if h.is_remote == remote]
        
        # Filter by skill level
        if skill_level:
            filtered_hackathons = [h for h in filtered_hackathons if h.skill_level == skill_level]
        
        # Filter by team size
        if team_size:
            filtered_hackathons = [h for h in filtered_hackathons if h.team_size == team_size or h.team_size == "both"]
        
        # Filter by keywords
        if keywords:
            filtered_hackathons = [
                h for h in filtered_hackathons 
                if any(kw.lower() in h.name.lower() or kw.lower() in h.description.lower() 
                      for kw in keywords)
            ]
        
        # Sort hackathons by start date (upcoming first)
        filtered_hackathons.sort(key=lambda x: x.start_date)
        
        return filtered_hackathons
    
    def get_personalized_recommendations(self, profile, limit=5):
        """
        Get personalized job and hackathon recommendations
        
        Args:
            profile (dict): User profile data
            limit (int): Maximum number of recommendations
            
        Returns:
            dict: Recommended jobs and hackathons
        """
        profile_text = self._profile_to_text(profile)
        profile_keywords = extract_keywords(profile_text, limit=10)
        
        # Get jobs matching the profile
        jobs = self.search_jobs(profile=profile)
        jobs = jobs[:limit]
        
        # Get hackathons based on skills
        hackathons = self.search_hackathons(keywords=profile_keywords)
        hackathons = hackathons[:limit]
        
        return {
            'jobs': jobs,
            'hackathons': hackathons
        }
    
    def _profile_to_text(self, profile):
        """Convert profile data to plain text for matching"""
        if not profile:
            return ""
        
        profile_text = ""
        
        # Personal info
        if 'personal_info' in profile:
            profile_text += profile['personal_info'].get('summary', '') + " "
        
        # Skills
        if 'skills' in profile:
            profile_text += " ".join(profile['skills']) + " "
        
        # Experience
        if 'experience' in profile:
            for exp in profile['experience']:
                profile_text += exp.get('title', '') + " " + exp.get('company', '') + " " + exp.get('description', '') + " "
                profile_text += " ".join(exp.get('responsibilities', [])) + " "
        
        # Projects
        if 'projects' in profile:
            for proj in profile['projects']:
                profile_text += proj.get('name', '') + " " + proj.get('description', '') + " "
                profile_text += " ".join(proj.get('technologies', [])) + " "
        
        return profile_text
    
    def _generate_mock_jobs(self):
        """
        Generate mock job data for demonstration
        
        Returns:
            list: Mock job opportunities
        """
        from models import JobOpportunity
        
        job_titles = [
            "Software Engineer", "Frontend Developer", "Backend Developer", 
            "Full Stack Developer", "Data Scientist", "DevOps Engineer",
            "Product Manager", "UX Designer", "QA Engineer", "ML Engineer"
        ]
        
        companies = [
            "TechCorp", "DataSys", "WebFront", "CloudScale", "AILabs",
            "DevForge", "CodeCraft", "ByteWorks", "QuantumTech", "PixelPerfect"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
            "Boston, MA", "Chicago, IL", "Remote", "Denver, CO", "Atlanta, GA",
            "Portland, OR"
        ]
        
        job_types = ["remote", "full-time", "part-time", "internship"]
        
        # Tech stack descriptions
        tech_stacks = [
            "Python, Django, PostgreSQL, AWS",
            "JavaScript, React, Node.js, MongoDB",
            "Java, Spring Boot, MySQL, Docker",
            "TypeScript, Angular, Express, Firebase",
            "Python, TensorFlow, PyTorch, Scikit-learn",
            "Kubernetes, Docker, Terraform, AWS",
            "Ruby, Rails, Redis, Heroku",
            "JavaScript, Vue.js, GraphQL, Postgres",
            "Golang, gRPC, Kubernetes, GCP",
            "C#, .NET Core, SQL Server, Azure"
        ]
        
        description_templates = [
            "We are looking for a talented {role} to join our team. You will work on {task} using {tech_stack}. The ideal candidate has experience with {requirement}.",
            "Join our team as a {role} and help us build {task}. You'll be working with {tech_stack}. We're looking for someone with {requirement}.",
            "Exciting opportunity for a {role} to contribute to {task}. Required skills: {tech_stack}. Experience with {requirement} is a plus.",
            "We need a skilled {role} to help us {task}. Our stack includes {tech_stack}. Must have experience with {requirement}."
        ]
        
        tasks = [
            "our core product", 
            "scalable web applications", 
            "machine learning models",
            "cloud infrastructure",
            "user-facing features",
            "internal tools",
            "data pipelines",
            "mobile applications",
            "payment systems",
            "e-commerce solutions"
        ]
        
        requirements = [
            "frontend frameworks", 
            "database optimization", 
            "cloud services",
            "CI/CD pipelines",
            "microservices",
            "RESTful APIs",
            "test-driven development",
            "agile methodologies",
            "distributed systems",
            "containerization"
        ]
        
        mock_jobs = []
        
        # Generate 20 mock jobs
        for i in range(20):
            job_title = random.choice(job_titles)
            company = random.choice(companies)
            location = random.choice(locations)
            job_type = random.choice(job_types)
            tech_stack = random.choice(tech_stacks)
            task = random.choice(tasks)
            requirement = random.choice(requirements)
            
            description_template = random.choice(description_templates)
            description = description_template.format(
                role=job_title, 
                task=task, 
                tech_stack=tech_stack, 
                requirement=requirement
            )
            
            # Generate a random posted date within the last 30 days
            days_ago = random.randint(0, 30)
            posted_date = datetime.now() - timedelta(days=days_ago)
            
            url = f"https://example.com/jobs/{i}"
            
            job = JobOpportunity(
                title=job_title,
                company=company,
                location=location,
                job_type=job_type,
                description=description,
                url=url,
                posted_date=posted_date
            )
            
            mock_jobs.append(job)
        
        return mock_jobs
    
    def _generate_mock_hackathons(self):
        """
        Generate mock hackathon data for demonstration
        
        Returns:
            list: Mock hackathon opportunities
        """
        from models import Hackathon
        
        hackathon_names = [
            "CodeFest", "HackVenture", "ByteHack", "DevChallenge", "AIHack",
            "CloudCraft", "DataDive", "WebBuilder", "MobileHacks", "GameJam"
        ]
        
        organizers = [
            "TechCommunity", "HackerCorp", "DevNetwork", "OpenSource Alliance",
            "CodeSchool", "StudentTech", "Industry Connect", "StartupHub",
            "TechGiants", "UniversityLabs"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
            "Boston, MA", "Online", "Chicago, IL", "Denver, CO", "Atlanta, GA",
            "London, UK"
        ]
        
        descriptions = [
            "A 48-hour hackathon where participants build innovative solutions for {focus_area}. Prizes for the best projects!",
            "Join us for a weekend of coding, collaboration, and creativity. This hackathon focuses on {focus_area}.",
            "Build something amazing for {focus_area} in just 24 hours. Open to coders of all skill levels.",
            "Put your skills to the test in this competitive hackathon. The theme is {focus_area}.",
            "A beginner-friendly hackathon exploring solutions for {focus_area}. Great networking opportunity!"
        ]
        
        focus_areas = [
            "healthcare tech", 
            "environmental sustainability", 
            "education technology",
            "financial inclusion",
            "smart cities",
            "artificial intelligence",
            "blockchain applications",
            "mobile accessibility",
            "gaming innovations",
            "social impact"
        ]
        
        skill_levels = ["beginner", "intermediate", "advanced"]
        team_sizes = ["individual", "team", "both"]
        
        mock_hackathons = []
        
        # Generate 20 mock hackathons
        for i in range(20):
            name = random.choice(hackathon_names) + " " + str(random.randint(1, 10))
            organizer = random.choice(organizers)
            location = random.choice(locations)
            is_remote = location == "Online" or random.choice([True, False])
            focus_area = random.choice(focus_areas)
            
            description_template = random.choice(descriptions)
            description = description_template.format(focus_area=focus_area)
            
            skill_level = random.choice(skill_levels)
            team_size = random.choice(team_sizes)
            
            # Generate random dates (some in the past, some in the future)
            days_offset = random.randint(-10, 60)  # From 10 days ago to 60 days in the future
            start_date = datetime.now() + timedelta(days=days_offset)
            end_date = start_date + timedelta(days=random.randint(1, 3))
            
            url = f"https://example.com/hackathons/{i}"
            
            prizes = []
            if random.choice([True, False]):
                prizes = [
                    f"1st Place: ${random.randint(1, 5) * 1000}",
                    f"2nd Place: ${random.randint(5, 10) * 100}",
                    f"3rd Place: ${random.randint(1, 5) * 100}"
                ]
            
            hackathon = Hackathon(
                name=name,
                organizer=organizer,
                location=location,
                start_date=start_date,
                end_date=end_date,
                description=description,
                url=url,
                is_remote=is_remote,
                skill_level=skill_level,
                team_size=team_size,
                prizes=prizes
            )
            
            mock_hackathons.append(hackathon)
        
        return mock_hackathons
