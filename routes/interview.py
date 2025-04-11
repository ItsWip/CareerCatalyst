from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from flask_login import login_required, current_user
from models import Interview
from utils.interview_simulator import InterviewSimulator
from utils.speech_utils import speech_to_text, text_to_speech, analyze_speech_characteristics
import base64

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/')
@login_required
def index():
    """Interview practice home page"""
    interviews = current_app.interviews.get(current_user.username, [])
    return render_template('interview/practice.html', interviews=interviews)

@interview_bp.route('/start', methods=['POST'])
@login_required
def start():
    """Start a new interview session"""
    role = request.form.get('role', 'Software Developer')
    mode = request.form.get('mode', 'text')
    job_description = request.form.get('job_description', '')
    
    # Create a new interview simulator
    simulator = InterviewSimulator(role=role, mode=mode)
    
    # Generate questions
    question_types = request.form.getlist('question_types[]')
    if not question_types:
        question_types = ['technical', 'behavioral', 'hr']
    
    num_questions = int(request.form.get('num_questions', 5))
    questions = simulator.generate_questions(
        job_description=job_description,
        question_types=question_types,
        num_questions=num_questions
    )
    
    # Store in session
    session['interview'] = {
        'role': role,
        'mode': mode,
        'job_description': job_description,
        'questions': questions,
        'current_index': 0,
        'answers': [None] * len(questions),
        'feedback': [None] * len(questions)
    }
    
    return jsonify({
        'success': True,
        'questions': questions,
        'current_question': questions[0] if questions else None
    })

@interview_bp.route('/next-question', methods=['POST'])
@login_required
def next_question():
    """Get the next interview question"""
    if 'interview' not in session:
        return jsonify({'success': False, 'message': 'No active interview session.'})
    
    interview = session['interview']
    current_index = interview['current_index'] + 1
    
    if current_index >= len(interview['questions']):
        return jsonify({
            'success': True,
            'finished': True,
            'message': 'Interview complete.'
        })
    
    interview['current_index'] = current_index
    session['interview'] = interview
    
    return jsonify({
        'success': True,
        'current_question': interview['questions'][current_index],
        'question_number': current_index + 1,
        'total_questions': len(interview['questions'])
    })

@interview_bp.route('/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit answer for the current question"""
    if 'interview' not in session:
        return jsonify({'success': False, 'message': 'No active interview session.'})
    
    interview = session['interview']
    current_index = interview['current_index']
    
    if current_index >= len(interview['questions']):
        return jsonify({'success': False, 'message': 'Interview already complete.'})
    
    answer_text = request.form.get('answer', '')
    question = interview['questions'][current_index]
    
    # Create simulator instance
    simulator = InterviewSimulator(role=interview['role'], mode=interview['mode'])
    
    # Analyze answer
    from utils.nlp_utils import analyze_answer
    feedback = analyze_answer(question, answer_text)
    
    # Store answer and feedback
    interview['answers'][current_index] = answer_text
    interview['feedback'][current_index] = feedback
    session['interview'] = interview
    
    return jsonify({
        'success': True,
        'feedback': feedback,
        'question_number': current_index + 1,
        'total_questions': len(interview['questions'])
    })

@interview_bp.route('/audio-answer', methods=['POST'])
@login_required
def audio_answer():
    """Process audio answer for the current question"""
    if 'interview' not in session:
        return jsonify({'success': False, 'message': 'No active interview session.'})
    
    interview = session['interview']
    current_index = interview['current_index']
    
    if current_index >= len(interview['questions']):
        return jsonify({'success': False, 'message': 'Interview already complete.'})
    
    # Get audio data
    audio_data = request.files.get('audio')
    if not audio_data:
        return jsonify({'success': False, 'message': 'No audio data received.'})
    
    # Convert speech to text
    audio_bytes = audio_data.read()
    try:
        text = speech_to_text(audio_bytes)
        
        # Analyze speech characteristics
        speech_analysis = analyze_speech_characteristics(audio_bytes)
        
        # Analyze answer content
        question = interview['questions'][current_index]
        from utils.nlp_utils import analyze_answer
        content_feedback = analyze_answer(question, text)
        
        # Combine feedback
        feedback = content_feedback
        feedback['speech_analysis'] = speech_analysis
        
        # Store answer and feedback
        interview['answers'][current_index] = text
        interview['feedback'][current_index] = feedback
        session['interview'] = interview
        
        return jsonify({
            'success': True,
            'transcribed_text': text,
            'feedback': feedback,
            'question_number': current_index + 1,
            'total_questions': len(interview['questions'])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing audio: {str(e)}'})

@interview_bp.route('/get-question-audio', methods=['GET'])
@login_required
def get_question_audio():
    """Get audio version of the current question"""
    if 'interview' not in session:
        return jsonify({'success': False, 'message': 'No active interview session.'})
    
    interview = session['interview']
    current_index = interview['current_index']
    
    if current_index >= len(interview['questions']):
        return jsonify({'success': False, 'message': 'Interview already complete.'})
    
    question_text = interview['questions'][current_index]
    
    # Convert question to speech
    try:
        audio_data = text_to_speech(question_text)
        if audio_data:
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            return jsonify({
                'success': True,
                'audio_data': encoded_audio
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to generate audio.'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating audio: {str(e)}'})

@interview_bp.route('/complete', methods=['POST'])
@login_required
def complete():
    """Complete the interview and save results"""
    if 'interview' not in session:
        return jsonify({'success': False, 'message': 'No active interview session.'})
    
    interview_data = session['interview']
    
    # Create Interview object
    interview = Interview(
        user_id=current_user.username,
        role=interview_data['role'],
        mode=interview_data['mode']
    )
    
    interview.questions = []
    for i, question in enumerate(interview_data['questions']):
        from models import Question
        q = Question(question, "general")  # Type will be refined later
        
        if i < len(interview_data['answers']) and interview_data['answers'][i]:
            q.answer = interview_data['answers'][i]
            q.feedback = interview_data['feedback'][i]
            
            # Calculate score
            if q.feedback:
                scores = [
                    q.feedback.get('clarity', 0),
                    q.feedback.get('relevance', 0),
                    q.feedback.get('confidence', 0)
                ]
                q.score = sum(scores) / len(scores) if scores else 0
        
        interview.questions.append(q)
    
    # Calculate overall score
    scores = [q.score for q in interview.questions if q.answer]
    interview.score = sum(scores) / len(scores) if scores else 0
    
    # Create a simulator to generate the summary
    simulator = InterviewSimulator(role=interview.role, mode=interview.mode)
    simulator.questions = interview_data['questions']
    simulator.answers = interview_data['answers']
    simulator.feedback = interview_data['feedback']
    
    # Generate overall feedback
    summary = simulator.complete_interview()
    interview.feedback = summary
    
    # Save to in-memory storage
    if current_user.username not in current_app.interviews:
        current_app.interviews[current_user.username] = []
    
    current_app.interviews[current_user.username].append(interview)
    
    # Clear session data
    session.pop('interview', None)
    
    return jsonify({
        'success': True,
        'interview_index': len(current_app.interviews[current_user.username]) - 1,
        'summary': summary
    })

@interview_bp.route('/history')
@login_required
def history():
    """View interview history"""
    interviews = current_app.interviews.get(current_user.username, [])
    return render_template('interview/history.html', interviews=interviews)

@interview_bp.route('/view/<int:index>')
@login_required
def view(index):
    """View a specific interview"""
    interviews = current_app.interviews.get(current_user.username, [])
    
    if index >= len(interviews):
        flash('Interview not found.', 'danger')
        return redirect(url_for('interview.history'))
    
    interview = interviews[index]
    return render_template('interview/history.html', interview=interview, interviews=interviews)

@interview_bp.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete(index):
    """Delete an interview"""
    interviews = current_app.interviews.get(current_user.username, [])
    
    if index >= len(interviews):
        return jsonify({'success': False, 'message': 'Interview not found.'})
    
    try:
        del interviews[index]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
