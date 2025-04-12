"""
Utility for conducting interviews using open-source LLMs.
Uses llama-cpp-python as the backend for inference with quantized models.
"""
import os
import json
import random

# Define sample questions by role and difficulty for fallback
SAMPLE_QUESTIONS = {
    "software_engineer": {
        "beginner": [
            {"text": "Explain the difference between a list and a tuple in Python.", "type": "technical"},
            {"text": "What is version control and why is it important?", "type": "technical"},
            {"text": "Describe a project you worked on that you're proud of.", "type": "behavioral"},
            {"text": "What made you interested in software engineering?", "type": "hr"}
        ],
        "intermediate": [
            {"text": "Explain the concept of time complexity and give examples of O(1), O(n), and O(n²) operations.", "type": "technical"},
            {"text": "How would you design a basic caching system?", "type": "technical"},
            {"text": "Tell me about a time you had to debug a complex issue. What was your approach?", "type": "behavioral"},
            {"text": "How do you stay updated with new technologies?", "type": "hr"}
        ],
        "advanced": [
            {"text": "Explain the CAP theorem and its implications for distributed systems.", "type": "technical"},
            {"text": "How would you optimize a database query that's performing slowly?", "type": "technical"},
            {"text": "Describe a situation where you had to make a difficult technical decision with limited information.", "type": "behavioral"},
            {"text": "How do you balance technical debt with feature development?", "type": "hr"}
        ],
        "expert": [
            {"text": "How would you design a globally distributed system with eventual consistency?", "type": "technical"},
            {"text": "Explain approaches to handle cascading failures in microservices architectures.", "type": "technical"},
            {"text": "Tell me about a time you led a major architectural change. How did you gain buy-in?", "type": "behavioral"},
            {"text": "How do you evaluate emerging technologies for potential adoption?", "type": "hr"}
        ]
    },
    "data_scientist": {
        "beginner": [
            {"text": "Explain the difference between supervised and unsupervised learning.", "type": "technical"},
            {"text": "What is the purpose of train/test splits in machine learning?", "type": "technical"},
            {"text": "Describe a data analysis project you've worked on.", "type": "behavioral"},
            {"text": "Why are you interested in data science?", "type": "hr"}
        ],
        "intermediate": [
            {"text": "Explain the bias-variance tradeoff.", "type": "technical"},
            {"text": "How would you handle imbalanced data in a classification problem?", "type": "technical"},
            {"text": "Tell me about a time when your analysis led to a surprising insight.", "type": "behavioral"},
            {"text": "How do you ensure your analysis is communicated effectively to non-technical stakeholders?", "type": "hr"}
        ]
    },
    # More roles can be added here with tailored questions
}

# Default general questions for any role not specifically defined
DEFAULT_QUESTIONS = {
    "beginner": [
        {"text": "What interests you about this field?", "type": "hr"},
        {"text": "What relevant coursework or projects have you completed?", "type": "technical"},
        {"text": "Tell me about yourself and your background.", "type": "hr"},
        {"text": "Describe a time you had to learn something quickly.", "type": "behavioral"}
    ],
    "intermediate": [
        {"text": "What are your greatest professional strengths and weaknesses?", "type": "hr"},
        {"text": "Describe a challenging project you worked on.", "type": "behavioral"},
        {"text": "How do you prioritize your work when you have multiple deadlines?", "type": "behavioral"},
        {"text": "What tools or methodologies do you use in your work?", "type": "technical"}
    ],
    "advanced": [
        {"text": "How have you mentored or coached others in your field?", "type": "behavioral"},
        {"text": "Describe a time when you had to solve a complex problem under pressure.", "type": "behavioral"},
        {"text": "How do you stay current in your field?", "type": "hr"},
        {"text": "What is the most innovative solution you've developed?", "type": "technical"}
    ],
    "expert": [
        {"text": "How have you influenced the strategic direction of your team or organization?", "type": "behavioral"},
        {"text": "Describe your approach to evaluating and adopting new technologies or methodologies.", "type": "technical"},
        {"text": "How do you balance technical leadership with business objectives?", "type": "hr"},
        {"text": "Tell me about a time you had to navigate significant organizational change.", "type": "behavioral"}
    ]
}

# Feedback templates based on score ranges
FEEDBACK_TEMPLATES = {
    "technical": {
        (0, 3): {
            "analysis": "Your answer lacks technical depth and contains some inaccuracies.",
            "strengths": [
                "Attempted to address the technical question",
                "Showed willingness to engage with complex concepts"
            ],
            "improvements": [
                "Study the fundamental concepts in this area",
                "Practice explaining technical concepts clearly and concisely",
                "Include specific examples to demonstrate understanding"
            ]
        },
        (4, 6): {
            "analysis": "Your answer demonstrates basic technical knowledge but could benefit from more depth and precision.",
            "strengths": [
                "Included some relevant technical concepts",
                "Attempted to structure your answer logically"
            ],
            "improvements": [
                "Deepen your understanding of the core principles",
                "Be more specific with technical terminology",
                "Add practical examples from your experience"
            ]
        },
        (7, 8): {
            "analysis": "Your answer shows good technical knowledge, but could be more comprehensive in addressing all aspects of the question.",
            "strengths": [
                "Good understanding of technical concepts",
                "Clear explanation of core principles",
                "Practical approach to the solution"
            ],
            "improvements": [
                "Provide more specific examples",
                "Consider discussing trade-offs in your approach",
                "Expand on the technical details"
            ]
        },
        (9, 10): {
            "analysis": "Your answer demonstrates excellent technical knowledge with depth, accuracy, and comprehensive coverage.",
            "strengths": [
                "Demonstrated deep technical understanding",
                "Provided clear, structured explanation",
                "Included relevant examples and trade-offs"
            ],
            "improvements": [
                "Consider additional edge cases or constraints",
                "Could further emphasize business impact",
                "Perhaps include alternative approaches for comparison"
            ]
        }
    },
    "behavioral": {
        (0, 3): {
            "analysis": "Your answer would benefit from a more structured approach and specific examples.",
            "strengths": [
                "Attempted to address the question",
                "Showed honesty in your reflection"
            ],
            "improvements": [
                "Use the STAR method (Situation, Task, Action, Result)",
                "Include specific, concrete examples from your experience",
                "Focus on your personal contribution and learnings"
            ]
        },
        (4, 6): {
            "analysis": "Your answer provides some good examples but could be more structured and results-focused.",
            "strengths": [
                "Shared relevant personal experiences",
                "Demonstrated some self-awareness"
            ],
            "improvements": [
                "Structure your response with the STAR method",
                "Highlight measurable results or impacts",
                "Be more concise in your storytelling"
            ]
        },
        (7, 8): {
            "analysis": "Your answer effectively uses the STAR method but could benefit from more emphasis on results and learnings.",
            "strengths": [
                "Used a relevant personal experience",
                "Structured your answer logically",
                "Showed problem-solving abilities"
            ],
            "improvements": [
                "Quantify your impact more specifically",
                "Elaborate on what you learned from the experience",
                "Connect the example more directly to the role"
            ]
        },
        (9, 10): {
            "analysis": "Your answer is excellent, with a clear structure, specific examples, and demonstrated impact.",
            "strengths": [
                "Provided a compelling, structured example",
                "Clearly articulated your specific actions",
                "Highlighted measurable results and personal growth"
            ],
            "improvements": [
                "Consider briefly mentioning alternative approaches",
                "Could further emphasize transferable skills",
                "Possibly connect to broader organizational impact"
            ]
        }
    },
    "hr": {
        (0, 3): {
            "analysis": "Your answer could benefit from more preparation and alignment with your career goals.",
            "strengths": [
                "Showed authentic interest in the position",
                "Attempted to share relevant information"
            ],
            "improvements": [
                "Research the role and company more thoroughly",
                "Prepare concise, focused responses to common questions",
                "Connect your background specifically to this position"
            ]
        },
        (4, 6): {
            "analysis": "Your answer shows good preparation but could be more specific about your fit for the role.",
            "strengths": [
                "Demonstrated knowledge about the position",
                "Shared relevant aspects of your background"
            ],
            "improvements": [
                "Be more specific about your career aspirations",
                "Highlight alignment between your values and company culture",
                "Prepare a more concise response"
            ]
        },
        (7, 8): {
            "analysis": "Your answer was professional and showed good alignment with the role, but could include more specific examples.",
            "strengths": [
                "Professional tone and attitude",
                "Clear connection between your background and the role",
                "Good understanding of role requirements"
            ],
            "improvements": [
                "Include more specific examples from your experience",
                "Be more concise in your key points",
                "Further emphasize cultural fit"
            ]
        },
        (9, 10): {
            "analysis": "Your answer demonstrates excellent preparation, self-awareness, and alignment with the role.",
            "strengths": [
                "Showed deep understanding of the role and company",
                "Articulated clear, relevant motivations",
                "Seamlessly connected past experience to future goals"
            ],
            "improvements": [
                "Consider adding brief mention of long-term vision",
                "Could further personalize to the specific company culture",
                "Perhaps share a brief anecdote for memorability"
            ]
        }
    }
}

def safe_llm_call(model, prompt, fallback_result):
    """Safely attempt to call the LLM, with fallback if it fails."""
    try:
        if model is None:
            # LLM not available
            raise ImportError("LLM not available")
        
        # Format the prompt with system instruction for better output
        formatted_prompt = f"""
        <s>[INST] <<SYS>>
        You are an expert interviewer and career coach assisting with job interviews. 
        Provide clear, honest, and constructive feedback.
        Always respond in the format requested, using valid JSON when asked to do so.
        <</SYS>>

        {prompt} [/INST]
        """
        
        # Call the LLM
        result = model.create_completion(
            formatted_prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.95,
            stop=["</s>", "[/INST]"],
            echo=False
        )
        
        # Extract text from response
        response_text = result.get('choices', [{}])[0].get('text', '').strip()
        
        if not response_text:
            raise ValueError("Empty response from LLM")
            
        return response_text
    
    except (ImportError, Exception) as e:
        print(f"LLM call failed: {str(e)}. Using fallback.")
        return fallback_result

class LLMInterviewer:
    """Class to handle interview simulation with LLM."""
    
    def __init__(self):
        """Initialize the LLM interviewer."""
        self.llm = None
        try:
            # Try to import and initialize the LLM
            # If the llama-cpp-python package is installed
            try:
                from llama_cpp import Llama
                
                # Check if model exists in models directory
                model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
                os.makedirs(model_dir, exist_ok=True)
                
                model_path = os.path.join(model_dir, "llama-2-7b-chat.Q4_K_M.gguf")
                
                # Check if model exists
                if os.path.exists(model_path):
                    print(f"Loading LLM model from {model_path}...")
                    self.llm = Llama(
                        model_path=model_path,
                        n_ctx=2048,
                        n_threads=4
                    )
                    print("LLM model loaded successfully")
                else:
                    print(f"Model file not found at {model_path}")
                    print("To use LLM features, download a GGUF model to the 'models' directory")
                    self.llm = None
            except ImportError:
                print("llama-cpp-python package not installed. LLM features will not be available.")
                print("Install with: pip install llama-cpp-python")
                self.llm = None
        except Exception as e:
            print(f"Unable to initialize LLM: {str(e)}")
            self.llm = None
    
    def generate_questions(self, job_role, difficulty, question_types, num_questions=5):
        """
        Generate interview questions tailored to the job role and difficulty.
        
        Args:
            job_role (str): The job role (e.g., "software_engineer")
            difficulty (str): The difficulty level (beginner, intermediate, advanced, expert)
            question_types (list): Types of questions to include (technical, behavioral, hr)
            num_questions (int): Number of questions to generate
            
        Returns:
            list: Generated questions with type information
        """
        # Prepare prompt for LLM
        prompt = f"""
        Generate {num_questions} interview questions for a {difficulty} level {job_role} position.
        
        Include questions of these types: {', '.join(question_types)}.
        
        Format your response as a JSON array of objects with 'text' and 'type' fields.
        Example:
        [
            {{"text": "What is your experience with...", "type": "behavioral"}},
            {{"text": "How would you implement...", "type": "technical"}},
            {{"text": "Why are you interested in...", "type": "hr"}}
        ]
        """
        
        # Prepare fallback questions
        fallback_questions = []
        
        # Get role-specific questions if available, otherwise use defaults
        role_questions = SAMPLE_QUESTIONS.get(job_role, DEFAULT_QUESTIONS)
        difficulty_questions = role_questions.get(difficulty, DEFAULT_QUESTIONS[difficulty])
        
        # Filter by requested question types
        filtered_questions = [q for q in difficulty_questions if q["type"] in question_types]
        
        # If we don't have enough role-specific questions, add from defaults
        if len(filtered_questions) < num_questions:
            default_filtered = [q for q in DEFAULT_QUESTIONS[difficulty] 
                                if q["type"] in question_types and q not in filtered_questions]
            filtered_questions.extend(default_filtered)
        
        # Shuffle and limit to requested number
        random.shuffle(filtered_questions)
        fallback_questions = filtered_questions[:num_questions]
        
        # Try to use LLM for generating questions
        llm_result = safe_llm_call(self.llm, prompt, json.dumps(fallback_questions))
        
        # Parse result if it's a string (from LLM)
        if isinstance(llm_result, str):
            try:
                # Extract JSON if embedded in text
                if '[' in llm_result and ']' in llm_result:
                    json_str = llm_result[llm_result.find('['):llm_result.rfind(']')+1]
                    questions = json.loads(json_str)
                else:
                    questions = json.loads(llm_result)
                
                # Validate structure
                for q in questions:
                    if not isinstance(q, dict) or 'text' not in q or 'type' not in q:
                        # Invalid structure, use fallback
                        return fallback_questions
                
                return questions[:num_questions]
            except json.JSONDecodeError:
                # If we can't parse JSON, use fallback
                return fallback_questions
        
        return fallback_questions
    
    def analyze_answer(self, question, answer, job_role, difficulty):
        """
        Analyze the answer to an interview question and provide feedback.
        
        Args:
            question (dict): The question object with text and type
            answer (str): The user's answer
            job_role (str): The job role being interviewed for
            difficulty (str): The difficulty level
            
        Returns:
            dict: Feedback including analysis, strengths, improvements, and score
        """
        # Prepare prompt for LLM
        prompt = f"""
        Evaluate this answer for a {difficulty} level {job_role} interview.
        
        Question ({question['type']}): {question['text']}
        
        Answer: {answer}
        
        Provide a detailed analysis of the answer, noting strengths and areas for improvement.
        Also assign a score from 0-10, where 10 is excellent.
        
        Format your response as a JSON object with 'analysis', 'strengths' (array), 'improvements' (array), and 'score' (number) fields.
        Example:
        {{
            "analysis": "The answer demonstrates...",
            "strengths": ["Clear explanation", "Good examples"],
            "improvements": ["Could be more concise", "Missing key concept X"],
            "score": 7
        }}
        """
        
        # Prepare fallback feedback based on simple heuristics
        score = 0
        question_type = question['type']
        
        # 1. Length-based scoring (basic proxy for thoroughness)
        if len(answer) > 300:
            score += 3
        elif len(answer) > 150:
            score += 2
        elif len(answer) > 50:
            score += 1
        
        # 2. Keyword-based scoring
        keyword_counts = {
            'technical': ['algorithm', 'code', 'system', 'design', 'implementation', 
                         'performance', 'complexity', 'architecture', 'solution', 'problem'],
            'behavioral': ['experience', 'team', 'project', 'challenge', 'solution', 
                          'learned', 'achievement', 'collaborate', 'lead', 'communicate'],
            'hr': ['background', 'interest', 'goal', 'motivation', 'strength', 
                  'weakness', 'value', 'culture', 'growth', 'opportunity']
        }
        
        keywords = keyword_counts.get(question_type, keyword_counts['hr'])
        keyword_matches = sum(1 for word in keywords if word in answer.lower())
        score += min(3, keyword_matches)
        
        # 3. Structure scoring (sentences, paragraphs)
        sentences = answer.split('.')
        if len(sentences) >= 5:
            score += 2
        elif len(sentences) >= 3:
            score += 1
        
        # 4. Difficulty adjustment
        difficulty_modifier = {
            'beginner': 0,
            'intermediate': -0.5,
            'advanced': -1,
            'expert': -1.5
        }
        
        score += difficulty_modifier.get(difficulty, 0)
        
        # Ensure score is between 0-10
        score = max(0, min(10, round(score)))
        
        # Get appropriate feedback template based on score
        for score_range, template in FEEDBACK_TEMPLATES[question_type].items():
            if score_range[0] <= score <= score_range[1]:
                feedback = {
                    "analysis": template["analysis"],
                    "strengths": template["strengths"],
                    "improvements": template["improvements"],
                    "score": score
                }
                break
        else:
            # Default feedback if no matching range
            feedback = {
                "analysis": "Your answer needs improvement in several areas.",
                "strengths": ["Attempted to address the question"],
                "improvements": ["Be more specific", "Structure your answer better", "Include relevant examples"],
                "score": score
            }
        
        # Try to use LLM for analyzing the answer
        llm_result = safe_llm_call(self.llm, prompt, json.dumps(feedback))
        
        # Parse result if it's a string (from LLM)
        if isinstance(llm_result, str):
            try:
                # Extract JSON if embedded in text
                if '{' in llm_result and '}' in llm_result:
                    json_str = llm_result[llm_result.find('{'):llm_result.rfind('}')+1]
                    result = json.loads(json_str)
                else:
                    result = json.loads(llm_result)
                
                # Validate structure
                required_keys = ['analysis', 'strengths', 'improvements', 'score']
                if all(key in result for key in required_keys):
                    if isinstance(result['score'], (int, float)) and 0 <= result['score'] <= 10:
                        return result
            except json.JSONDecodeError:
                # If we can't parse JSON, use fallback
                pass
        
        return feedback