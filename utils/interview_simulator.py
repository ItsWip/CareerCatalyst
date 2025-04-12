import logging
import random
from datetime import datetime
from utils.nlp_utils import generate_interview_questions, analyze_answer
from utils.speech_utils import text_to_speech

class InterviewSimulator:
    """Class to handle interview simulation functionality"""
    
    def __init__(self, role=None, mode="text"):
        self.role = role or "Software Developer"
        self.mode = mode  # "text" or "audio"
        self.questions = []
        self.current_question_index = 0
        self.answers = []
        self.feedback = []
        self.overall_score = 0
        self.start_time = datetime.now()
        self.end_time = None
    
    def generate_questions(self, job_description=None, question_types=None, num_questions=5):
        """
        Generate interview questions
        
        Args:
            job_description (str): Job description to base questions on
            question_types (list): Types of questions to include
            num_questions (int): Number of questions to generate
            
        Returns:
            list: Generated questions
        """
        if not question_types:
            question_types = ["technical", "behavioral", "hr"]
        
        # Default job description if none provided
        if not job_description:
            job_description = f"We are looking for a {self.role} with excellent technical skills and good communication abilities."
        
        all_questions = []
        
        # Generate questions for each type
        for q_type in question_types:
            type_questions = generate_interview_questions(
                job_description, 
                question_type=q_type,
                num_questions=num_questions
            )
            all_questions.extend(type_questions)
        
        # Shuffle and limit questions
        random.shuffle(all_questions)
        self.questions = all_questions[:num_questions]
        self.current_question_index = 0
        self.answers = [None] * len(self.questions)
        self.feedback = [None] * len(self.questions)
        
        return self.questions
    
    def get_current_question(self):
        """Get the current question"""
        if not self.questions or self.current_question_index >= len(self.questions):
            return None
        
        return self.questions[self.current_question_index]
    
    def get_next_question(self):
        """Move to the next question and return it"""
        self.current_question_index += 1
        return self.get_current_question()
    
    def submit_answer(self, answer_text):
        """
        Submit answer for the current question
        
        Args:
            answer_text (str): User's answer
            
        Returns:
            dict: Feedback on the answer
        """
        if not self.questions or self.current_question_index >= len(self.questions):
            return {"error": "No active question"}
        
        current_question = self.questions[self.current_question_index]
        
        # Analyze the answer
        feedback = analyze_answer(current_question, answer_text)
        
        # Store the answer and feedback
        self.answers[self.current_question_index] = answer_text
        self.feedback[self.current_question_index] = feedback
        
        return feedback
    
    def get_audio_for_question(self, question_index=None):
        """
        Get audio version of the question
        
        Args:
            question_index (int): Index of the question (default: current)
            
        Returns:
            bytes: Audio data
        """
        if question_index is None:
            question_index = self.current_question_index
        
        if not self.questions or question_index >= len(self.questions):
            return None
        
        question_text = self.questions[question_index]
        try:
            from utils.speech_utils import text_to_speech
            return text_to_speech(question_text)
        except Exception as e:
            logging.error(f"Error generating audio: {str(e)}")
            return None
    
    def complete_interview(self):
        """
        Complete the interview and generate summary
        
        Returns:
            dict: Interview summary
        """
        self.end_time = datetime.now()
        
        # Calculate overall score
        scores = []
        for fb in self.feedback:
            if fb:
                avg_score = (fb.get('clarity', 0) + fb.get('relevance', 0) + fb.get('confidence', 0)) / 3
                scores.append(avg_score)
        
        if scores:
            self.overall_score = sum(scores) / len(scores)
        
        # Generate interview summary
        summary = {
            'role': self.role,
            'mode': self.mode,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': (self.end_time - self.start_time).total_seconds() / 60,  # Minutes
            'num_questions': len(self.questions),
            'questions_answered': sum(1 for a in self.answers if a),
            'overall_score': round(self.overall_score, 2),
            'questions_and_answers': []
        }
        
        # Add detailed Q&A
        for i in range(len(self.questions)):
            if i < len(self.answers) and self.answers[i]:
                qa_item = {
                    'question': self.questions[i],
                    'answer': self.answers[i],
                    'feedback': self.feedback[i] if i < len(self.feedback) else None
                }
                summary['questions_and_answers'].append(qa_item)
        
        # Generate overall feedback
        if self.overall_score >= 8:
            summary['overall_feedback'] = "Excellent interview! You demonstrated strong communication skills and provided thorough and relevant answers."
        elif self.overall_score >= 6:
            summary['overall_feedback'] = "Good interview. Your answers were mostly on point, but there's room for improvement in clarity and detail."
        else:
            summary['overall_feedback'] = "You need more practice. Focus on providing more detailed and relevant answers, and work on your confidence."
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        clarity_scores = [fb.get('clarity', 0) for fb in self.feedback if fb]
        relevance_scores = [fb.get('relevance', 0) for fb in self.feedback if fb]
        confidence_scores = [fb.get('confidence', 0) for fb in self.feedback if fb]
        
        if clarity_scores and sum(clarity_scores) / len(clarity_scores) >= 7:
            strengths.append("Clear and concise communication")
        elif clarity_scores:
            weaknesses.append("Clarity in responses")
        
        if relevance_scores and sum(relevance_scores) / len(relevance_scores) >= 7:
            strengths.append("Providing relevant information")
        elif relevance_scores:
            weaknesses.append("Staying on topic and addressing questions directly")
        
        if confidence_scores and sum(confidence_scores) / len(confidence_scores) >= 7:
            strengths.append("Confident communication")
        elif confidence_scores:
            weaknesses.append("Confidence in your responses")
        
        summary['strengths'] = strengths
        summary['areas_for_improvement'] = weaknesses
        
        return summary
