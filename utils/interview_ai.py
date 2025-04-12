import random
import re

# Sample question templates for different interview types
HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why are you interested in this role?",
    "Why do you want to work for our company?",
    "What are your greatest strengths?",
    "What do you consider to be your weaknesses?",
    "Where do you see yourself in 5 years?",
    "Describe a challenging work situation and how you overcame it.",
    "How do you handle stress and pressure?",
    "What is your ideal work environment?",
    "How would your previous colleagues describe you?",
    "Why are you leaving your current job?",
    "What motivates you in your career?",
    "How do you prioritize your work?",
    "What are your salary expectations?",
    "Do you have any questions for us?"
]

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time when you had to deal with a difficult team member.",
    "Describe a situation where you had to meet a tight deadline.",
    "Give an example of a time when you showed leadership.",
    "Tell me about a time when you failed and what you learned from it.",
    "Describe a situation where you had to learn something quickly.",
    "Tell me about a time when you had to make a difficult decision.",
    "Give an example of how you handled a conflict with a colleague or supervisor.",
    "Describe a situation where you went above and beyond what was expected.",
    "Tell me about a time when you had to persuade someone to see things your way.",
    "Give an example of a time when you had to adapt to a significant change at work.",
    "Describe your biggest professional achievement and how you accomplished it.",
    "Tell me about a time when you received constructive criticism and how you responded.",
    "Give an example of how you have contributed to a team's success.",
    "Describe a situation where you had to solve a complex problem.",
    "Tell me about a time when you had to work with people from different backgrounds."
]

# Technical questions by role (simplified examples)
TECHNICAL_QUESTIONS = {
    "software developer": [
        "Explain the difference between an array and a linked list.",
        "What is object-oriented programming?",
        "How would you optimize a slow-performing query in a database?",
        "Explain what RESTful API is and its principles.",
        "What testing methodologies are you familiar with?",
        "Describe the MVC architecture pattern.",
        "How do you handle version control in your projects?",
        "What is the difference between HTTP and HTTPS?",
        "Explain the concept of dependency injection.",
        "How do you ensure your code is secure?",
        "What is the difference between synchronous and asynchronous programming?",
        "How would you debug a production issue?",
        "Explain the concept of memory leaks and how to prevent them.",
        "What's your approach to code reviews?",
        "How do you stay updated with the latest technologies?"
    ],
    "data scientist": [
        "Explain the difference between supervised and unsupervised learning.",
        "What is overfitting and how can you prevent it?",
        "How would you handle missing data in a dataset?",
        "Explain the bias-variance tradeoff.",
        "What are feature selection and feature engineering?",
        "Describe the difference between classification and regression problems.",
        "How would you evaluate a classification model's performance?",
        "What is the curse of dimensionality?",
        "Explain gradient descent algorithm.",
        "What's the difference between bagging and boosting?",
        "How would you handle imbalanced data?",
        "Explain cross-validation and why it's important.",
        "What is regularization and when would you use it?",
        "Describe your approach to A/B testing.",
        "How do you communicate complex findings to non-technical stakeholders?"
    ],
    "product manager": [
        "How do you prioritize features in your product roadmap?",
        "Describe how you would gather and incorporate user feedback.",
        "How do you measure the success of a product?",
        "What's your approach to working with engineering teams?",
        "How do you balance user needs with business objectives?",
        "Describe a product you managed from conception to launch.",
        "How do you handle scope creep?",
        "What metrics do you track for your products?",
        "How do you validate new product ideas?",
        "Describe how you would handle a situation where engineering says a feature is technically infeasible.",
        "How do you decide when to pivot a product strategy?",
        "What methodologies do you use for product development?",
        "How do you communicate product vision to different stakeholders?",
        "Describe your approach to competitor analysis.",
        "How do you balance short-term fixes with long-term product goals?"
    ],
    "ux designer": [
        "Describe your design process from research to delivery.",
        "How do you advocate for user needs in your organization?",
        "What methods do you use for user research?",
        "How do you validate your design solutions?",
        "Describe a time when you had to compromise on a design decision.",
        "How do you handle design feedback from stakeholders?",
        "What design tools do you use and why?",
        "How do you ensure accessibility in your designs?",
        "Describe how you apply design principles in your work.",
        "How do you balance aesthetics with usability?",
        "What's your approach to creating design systems?",
        "How do you design for different platforms (web, mobile, etc.)?",
        "Describe a complex UX problem you solved and your approach.",
        "How do you stay updated with design trends and technologies?",
        "How do you measure the success of your designs?"
    ]
}

# Generic technical questions for roles not in the list
GENERIC_TECHNICAL_QUESTIONS = [
    "What technical skills are you most proficient in?",
    "How do you stay updated with the latest developments in your field?",
    "What relevant certifications do you have?",
    "Describe a technical challenge you faced and how you overcame it.",
    "How do you approach learning new technologies or tools?",
    "What tools or software are you most comfortable using?",
    "How do you ensure the quality of your work?",
    "What methodologies are you familiar with in your field?",
    "Describe your process for solving complex problems.",
    "How do you handle technical disagreements with colleagues?",
    "What experience do you have with teamwork in technical projects?",
    "How do you document your work for others to understand?",
    "What metrics do you use to evaluate your performance?",
    "How do you prioritize tasks in a technical project?",
    "Describe a situation where you had to explain technical concepts to non-technical stakeholders."
]

def generate_interview_questions(job_role, interview_type, num_questions=5):
    """
    Generate interview questions based on the job role and interview type.
    
    Args:
        job_role (str): The job role/position
        interview_type (str): Type of interview (HR, Technical, Behavioral)
        num_questions (int): Number of questions to generate
        
    Returns:
        list: List of interview questions
    """
    questions = []
    
    # Normalize inputs
    job_role = job_role.lower() if job_role else ""
    interview_type = interview_type.lower() if interview_type else "hr"
    
    # Select questions based on interview type
    if interview_type == "technical":
        if job_role in TECHNICAL_QUESTIONS:
            role_questions = TECHNICAL_QUESTIONS[job_role]
        else:
            # Use generic technical questions for unrecognized roles
            role_questions = GENERIC_TECHNICAL_QUESTIONS
            
        # Add some role-specific questions
        questions = random.sample(role_questions, min(num_questions, len(role_questions)))
    
    elif interview_type == "behavioral":
        questions = random.sample(BEHAVIORAL_QUESTIONS, min(num_questions, len(BEHAVIORAL_QUESTIONS)))
    
    else:  # Default to HR questions
        questions = random.sample(HR_QUESTIONS, min(num_questions, len(HR_QUESTIONS)))
    
    # If we don't have enough questions, add some from the HR category
    if len(questions) < num_questions:
        additional_questions = random.sample(HR_QUESTIONS, num_questions - len(questions))
        questions.extend(additional_questions)
    
    return questions

def analyze_answer(question, answer):
    """
    Analyze the answer to an interview question and provide feedback.
    
    Args:
        question (str): The interview question
        answer (str): The user's answer
        
    Returns:
        tuple: (feedback, score) - Feedback string and score (0-10)
    """
    # Basic check for answer length
    if not answer or len(answer) < 20:
        return "Your answer is too brief. Try to provide more details and context.", 3
    
    # Check for answer structure and content
    feedback_points = []
    score = 7  # Start with a default score
    
    # Length check (more sophisticated)
    word_count = len(answer.split())
    if word_count < 30:
        feedback_points.append("Your answer could be more detailed.")
        score -= 1
    elif word_count > 500:
        feedback_points.append("Your answer is quite lengthy. Consider being more concise while maintaining key points.")
        score -= 0.5
    
    # Check for use of specific examples
    if not re.search(r'(for example|for instance|e\.g\.|specifically|in particular|in my experience)', answer, re.IGNORECASE):
        feedback_points.append("Consider including specific examples to strengthen your answer.")
        score -= 1
    
    # Check for filler words
    filler_words = ['um', 'uh', 'like', 'you know', 'sort of', 'kind of']
    filler_count = sum(1 for word in filler_words if re.search(r'\b' + word + r'\b', answer, re.IGNORECASE))
    if filler_count > 3:
        feedback_points.append("Try to reduce the use of filler words like 'um', 'uh', 'like', etc.")
        score -= 1
    
    # Check for STAR method elements in behavioral questions
    if any(x in question.lower() for x in ['tell me about a time', 'describe a situation', 'give an example']):
        star_elements = {
            'situation': ['situation', 'context', 'background', 'setting'],
            'task': ['task', 'responsibility', 'assignment', 'charged with', 'needed to', 'had to'],
            'action': ['action', 'approach', 'steps', 'procedure', 'initiative', 'implemented', 'executed', 'performed'],
            'result': ['result', 'outcome', 'achievement', 'accomplishment', 'impact', 'effect', 'led to', 'concluded with']
        }
        
        missing_elements = []
        for element, keywords in star_elements.items():
            if not any(re.search(r'\b' + keyword + r'\b', answer, re.IGNORECASE) for keyword in keywords):
                missing_elements.append(element)
        
        if missing_elements:
            elements_str = ', '.join(missing_elements)
            feedback_points.append(f"Your answer could be strengthened by clearly addressing the {elements_str} part(s) of the STAR method (Situation, Task, Action, Result).")
            score -= len(missing_elements) * 0.5
    
    # Check for positivity in discussing challenges or weaknesses
    if any(x in question.lower() for x in ['weakness', 'difficult', 'challenging', 'failed', 'mistake']):
        positive_words = ['learned', 'improved', 'growth', 'development', 'opportunity', 'overcome', 'solution']
        if not any(re.search(r'\b' + word + r'\b', answer, re.IGNORECASE) for word in positive_words):
            feedback_points.append("When discussing challenges or weaknesses, try to include how you've grown or what you've learned from them.")
            score -= 1
    
    # Format the feedback
    if feedback_points:
        feedback = "Feedback: " + " ".join(feedback_points)
    else:
        feedback = "Good job! Your answer was well-structured and addressed the question effectively."
        score += 1
    
    # Ensure score is within bounds
    score = max(1, min(10, score))
    
    return feedback, score
