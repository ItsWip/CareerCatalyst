import re
import logging
from collections import Counter

# Simple NLP alternatives while spaCy is unavailable
logging.warning("Using simplified NLP functions without spaCy")

def _tokenize(text):
    """Simple tokenization function"""
    # Convert to lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Split by whitespace
    return text.split()

def extract_keywords(text, limit=20):
    """
    Extract key terms from the job description using simple tokenization
    
    Args:
        text (str): Text to extract keywords from
        limit (int): Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple stopwords list
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
                'when', 'where', 'how', 'who', 'which', 'this', 'that', 'to', 'in', 
                'for', 'with', 'by', 'at', 'of', 'from', 'about', 'is', 'are', 'was', 
                'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 
                'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 
                'might', 'must', 'on', 'our', 'your', 'my', 'ours', 'yours', 'their', 'his', 'her'}
    
    # Tokenize text
    tokens = _tokenize(text)
    
    # Filter tokens
    keywords = [token for token in tokens if token not in stopwords and len(token) > 2]
    
    # Extract technical terms and skills
    tech_pattern = r'\b(python|java|javascript|html|css|react|angular|node\.js|sql|nosql|mongodb|aws|azure|docker|kubernetes|machine learning|ai|data science|agile|scrum|devops|ci/cd)\b'
    tech_keywords = re.findall(tech_pattern, text.lower())
    keywords.extend(tech_keywords)
    
    # Count occurrences and take the most frequent
    keyword_counter = Counter(keywords)
    top_keywords = [keyword for keyword, _ in keyword_counter.most_common(limit)]
    
    return top_keywords

def calculate_match_score(profile_text, job_text):
    """
    Calculate match score between profile and job description
    
    Args:
        profile_text (str): Text from user profile
        job_text (str): Text from job description
        
    Returns:
        float: Match score (0-100)
    """
    if not profile_text or not job_text:
        return 0
    
    # Extract keywords from both texts
    profile_keywords = extract_keywords(profile_text, limit=50)
    job_keywords = extract_keywords(job_text, limit=50)
    
    if not profile_keywords or not job_keywords:
        return 0
    
    # Calculate matches
    matches = sum(1 for keyword in profile_keywords if keyword in job_keywords)
    
    # Calculate score (percentage of job keywords found in profile)
    if len(job_keywords) > 0:
        score = (matches / len(job_keywords)) * 100
    else:
        score = 0
    
    return round(score, 2)

def suggest_resume_improvements(profile_text, job_text):
    """
    Suggest improvements for resume based on job description
    
    Args:
        profile_text (str): Text from user profile
        job_text (str): Text from job description
        
    Returns:
        dict: Suggestions for improvements
    """
    job_keywords = extract_keywords(job_text, limit=30)
    profile_keywords = extract_keywords(profile_text, limit=50)
    
    missing_keywords = [kw for kw in job_keywords if kw not in profile_keywords]
    
    suggestions = {
        "missing_keywords": missing_keywords[:10],  # Top 10 missing keywords
        "recommendations": []
    }
    
    # Generate recommendations
    if len(missing_keywords) > 0:
        suggestions["recommendations"].append(
            "Consider adding these skills to your profile: " + ", ".join(missing_keywords[:5])
        )
    
    # Check for specific terms
    leadership_terms = ["lead", "manage", "coordinate", "direct", "supervise"]
    if any(term in job_text.lower() for term in leadership_terms) and not any(term in profile_text.lower() for term in leadership_terms):
        suggestions["recommendations"].append(
            "The job requires leadership skills. Highlight any leadership experience."
        )
    
    teamwork_terms = ["team", "collaborate", "cooperation", "group"]
    if any(term in job_text.lower() for term in teamwork_terms) and not any(term in profile_text.lower() for term in teamwork_terms):
        suggestions["recommendations"].append(
            "Emphasize your teamwork experience in your profile."
        )
    
    return suggestions

def generate_interview_questions(job_text, question_type="all", num_questions=5):
    """
    Generate interview questions based on job description
    
    Args:
        job_text (str): Job description
        question_type (str): Type of questions (technical, behavioral, hr, all)
        num_questions (int): Number of questions to generate
        
    Returns:
        list: Generated questions
    """
    # Default questions by type
    technical_questions = [
        "Can you explain your experience with {technology}?",
        "How would you solve {problem} using {technology}?",
        "Describe a challenging technical project you've worked on.",
        "How do you stay updated with the latest developments in your field?",
        "What is your approach to debugging complex issues?",
        "Explain how you would design a system for {use_case}.",
        "What experience do you have with {methodology}?",
        "How would you implement {feature} for a large-scale system?",
        "Describe your experience with cloud platforms like AWS or Azure.",
        "How do you ensure code quality in your projects?"
    ]
    
    behavioral_questions = [
        "Describe a situation where you had to meet a tight deadline.",
        "Tell me about a time when you had to resolve a conflict in a team.",
        "How do you handle feedback and criticism?",
        "Describe a situation where you had to learn something quickly.",
        "Tell me about a time when you demonstrated leadership.",
        "How do you prioritize tasks when you have multiple deadlines?",
        "Describe a situation where you failed and what you learned from it.",
        "How do you handle working under pressure?",
        "Tell me about a time when you went above and beyond.",
        "How do you adapt to changing requirements?"
    ]
    
    hr_questions = [
        "Why are you interested in this position?",
        "Where do you see yourself in 5 years?",
        "What are your salary expectations?",
        "Why do you want to leave your current job?",
        "What are your strengths and weaknesses?",
        "How would your colleagues describe you?",
        "What motivates you at work?",
        "How do you define success?",
        "Why should we hire you?",
        "Do you have any questions for us?"
    ]
    
    # Extract keywords to customize questions
    keywords = extract_keywords(job_text, limit=10)
    technologies = [kw for kw in keywords if re.match(r'\b(python|java|javascript|html|css|react|angular|node\.js|sql|nosql|mongodb|aws|azure|docker|kubernetes)\b', kw)]
    methodologies = [kw for kw in keywords if kw in ["agile", "scrum", "waterfall", "devops", "kanban", "ci/cd"]]
    
    # Customize questions
    customized_technical = []
    for q in technical_questions:
        if "{technology}" in q and technologies:
            customized_technical.append(q.replace("{technology}", technologies[0]))
        elif "{methodology}" in q and methodologies:
            customized_technical.append(q.replace("{methodology}", methodologies[0]))
        elif "{problem}" in q:
            customized_technical.append(q.replace("{problem}", "performance optimization"))
        elif "{use_case}" in q:
            customized_technical.append(q.replace("{use_case}", "user authentication"))
        elif "{feature}" in q:
            customized_technical.append(q.replace("{feature}", "data synchronization"))
        else:
            customized_technical.append(q)
    
    # Select questions based on type
    questions = []
    if question_type == "technical" or question_type == "all":
        questions.extend(customized_technical[:num_questions])
    if question_type == "behavioral" or question_type == "all":
        questions.extend(behavioral_questions[:num_questions])
    if question_type == "hr" or question_type == "all":
        questions.extend(hr_questions[:num_questions])
    
    # If all types are requested, balance the selection
    if question_type == "all":
        # Aim for balanced distribution
        per_type = max(1, num_questions // 3)
        questions = (customized_technical[:per_type] + 
                     behavioral_questions[:per_type] + 
                     hr_questions[:per_type])
    
    return questions[:num_questions]

def analyze_answer(question, answer):
    """
    Analyze interview answer and provide feedback using simple text analysis
    
    Args:
        question (str): Interview question
        answer (str): User's answer
        
    Returns:
        dict: Feedback on the answer
    """
    if not answer:
        return {
            "clarity": 0,
            "relevance": 0,
            "confidence": 0,
            "feedback": "No answer provided.",
            "improvement_tips": ["Please provide an answer to receive feedback."]
        }
    
    # Calculate metrics
    word_count = len(answer.split())
    
    # Simple sentence detection
    sentence_count = len([s for s in re.split(r'[.!?]+', answer) if s.strip()])
    
    # Prepare feedback
    feedback = {
        "clarity": 0,
        "relevance": 0,
        "confidence": 0,
        "feedback": "",
        "improvement_tips": []
    }
    
    # Check answer length
    if word_count < 30:
        feedback["clarity"] = 3
        feedback["feedback"] = "Your answer is too brief."
        feedback["improvement_tips"].append("Elaborate more on your experience and skills.")
    elif word_count > 300:
        feedback["clarity"] = 6
        feedback["feedback"] = "Your answer is quite lengthy."
        feedback["improvement_tips"].append("Try to be more concise while maintaining detail.")
    else:
        feedback["clarity"] = 8
        feedback["feedback"] = "Your answer has good length."
    
    # Simple relevance check (keyword overlap)
    question_tokens = _tokenize(question)
    answer_tokens = _tokenize(answer)
    
    # Remove stopwords
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
               'when', 'where', 'how', 'who', 'which', 'this', 'that', 'to', 'in'}
    
    question_keywords = [t for t in question_tokens if t not in stopwords and len(t) > 2]
    answer_keywords = [t for t in answer_tokens if t not in stopwords and len(t) > 2]
    
    # Calculate keyword overlap
    overlap = sum(1 for kw in question_keywords if kw in answer_keywords)
    if question_keywords:
        relevance_score = min(10, (overlap / len(question_keywords)) * 10)
    else:
        relevance_score = 5
    
    feedback["relevance"] = round(relevance_score)
    
    if feedback["relevance"] < 5:
        feedback["improvement_tips"].append("Your answer doesn't fully address the question. Try to focus more on what was asked.")
    
    # Check confidence markers
    confidence_boosters = ["confident", "accomplished", "successful", "achieved", "led", "managed", "expertise", "proficient"]
    confidence_detractors = ["maybe", "perhaps", "try", "might", "could", "possibly", "i think", "not sure"]
    
    boosters_found = sum(1 for term in confidence_boosters if term in answer.lower())
    detractors_found = sum(1 for term in confidence_detractors if term in answer.lower())
    
    confidence_score = 7 + min(3, boosters_found) - min(4, detractors_found)
    feedback["confidence"] = max(1, min(10, confidence_score))
    
    if detractors_found > 1:
        feedback["improvement_tips"].append("Try to avoid uncertain phrases like 'maybe', 'perhaps', or 'I think'.")
    
    # Overall score and feedback
    overall_score = (feedback["clarity"] + feedback["relevance"] + feedback["confidence"]) / 3
    
    if overall_score >= 8:
        feedback["feedback"] = "Excellent answer! " + feedback["feedback"]
    elif overall_score >= 6:
        feedback["feedback"] = "Good answer. " + feedback["feedback"]
    else:
        feedback["feedback"] = "Your answer needs improvement. " + feedback["feedback"]
    
    return feedback
