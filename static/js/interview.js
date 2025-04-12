// Interview simulation functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize interview simulator
    const startInterviewBtn = document.getElementById('start-interview-btn');
    const interviewForm = document.getElementById('interview-setup-form');
    const interviewContainer = document.getElementById('interview-container');
    const questionContainer = document.getElementById('question-container');
    const answerContainer = document.getElementById('answer-container');
    const feedbackContainer = document.getElementById('feedback-container');
    const nextQuestionBtn = document.getElementById('next-question-btn');
    const finishInterviewBtn = document.getElementById('finish-interview-btn');
    const progressIndicator = document.getElementById('progress-indicator');
    const currentQuestionSpan = document.getElementById('current-question');
    const totalQuestionsSpan = document.getElementById('total-questions');
    
    let currentQuestion = 0;
    let totalQuestions = 0;
    let interviewMode = 'text';
    let mediaRecorder = null;
    let audioChunks = [];
    
    // Audio recording setup
    function setupAudioRecording() {
        const startRecordingBtn = document.getElementById('start-recording-btn');
        const stopRecordingBtn = document.getElementById('stop-recording-btn');
        const audioPlaybackContainer = document.getElementById('audio-playback-container');
        
        if (!startRecordingBtn || !stopRecordingBtn) return;
        
        // Request microphone access
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                // Enable recording button
                startRecordingBtn.disabled = false;
                
                // Setup recorder
                startRecordingBtn.addEventListener('click', function() {
                    // Show recording UI
                    startRecordingBtn.style.display = 'none';
                    stopRecordingBtn.style.display = 'inline-block';
                    audioChunks = [];
                    
                    // Create new recorder
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.addEventListener('dataavailable', event => {
                        audioChunks.push(event.data);
                    });
                    
                    mediaRecorder.addEventListener('stop', () => {
                        // Create blob and audio element for playback
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        // Display audio playback
                        audioPlaybackContainer.innerHTML = `
                            <audio controls src="${audioUrl}" class="w-100 mb-3"></audio>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-outline-danger me-2" id="discard-recording-btn">
                                    <i class="fas fa-trash"></i> Discard
                                </button>
                                <button class="btn btn-primary" id="submit-recording-btn">
                                    <i class="fas fa-paper-plane"></i> Submit Answer
                                </button>
                            </div>
                        `;
                        
                        // Setup discard button
                        document.getElementById('discard-recording-btn').addEventListener('click', function() {
                            audioPlaybackContainer.innerHTML = '';
                            startRecordingBtn.style.display = 'inline-block';
                            stopRecordingBtn.style.display = 'none';
                        });
                        
                        // Setup submit button
                        document.getElementById('submit-recording-btn').addEventListener('click', function() {
                            // Create form data with audio blob
                            const formData = new FormData();
                            formData.append('audio', audioBlob);
                            
                            // Show loading state
                            this.disabled = true;
                            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                            
                            // Submit audio answer
                            fetch('/interview/audio-answer', {
                                method: 'POST',
                                body: formData
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Show transcribed text
                                    const textAnswerElem = document.getElementById('text-answer');
                                    if (textAnswerElem) {
                                        textAnswerElem.value = data.transcribed_text;
                                    }
                                    
                                    // Display feedback
                                    displayFeedback(data.feedback);
                                    
                                    // Update progress
                                    updateProgress(data.question_number, data.total_questions);
                                    
                                    // Reset audio recording UI
                                    audioPlaybackContainer.innerHTML = '';
                                    startRecordingBtn.style.display = 'inline-block';
                                    stopRecordingBtn.style.display = 'none';
                                } else {
                                    showAlert(`Error: ${data.message}`, 'danger');
                                }
                            })
                            .catch(error => {
                                showAlert(`Error: ${error}`, 'danger');
                            });
                        });
                    });
                    
                    // Start recording
                    mediaRecorder.start();
                });
                
                // Setup stop recording button
                stopRecordingBtn.addEventListener('click', function() {
                    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                        mediaRecorder.stop();
                    }
                });
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                showAlert('Could not access microphone. Please ensure you have granted microphone permissions.', 'danger');
                // Disable audio mode
                document.getElementById('mode-text').checked = true;
                document.getElementById('mode-audio').disabled = true;
            });
    }
    
    // Start interview
    if (interviewForm) {
        interviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const role = document.getElementById('role').value;
            interviewMode = document.querySelector('input[name="mode"]:checked').value;
            const jobDescription = document.getElementById('job_description').value;
            const questionTypes = Array.from(document.querySelectorAll('input[name="question_types[]"]:checked')).map(cb => cb.value);
            const numQuestions = document.getElementById('num_questions').value;
            
            // Validate
            if (!role) {
                showAlert('Please enter a role.', 'warning');
                return;
            }
            
            if (questionTypes.length === 0) {
                showAlert('Please select at least one question type.', 'warning');
                return;
            }
            
            // Show loading state
            startInterviewBtn.disabled = true;
            startInterviewBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
            
            // Prepare data
            const formData = new FormData();
            formData.append('role', role);
            formData.append('mode', interviewMode);
            formData.append('job_description', jobDescription);
            questionTypes.forEach(type => {
                formData.append('question_types[]', type);
            });
            formData.append('num_questions', numQuestions);
            
            // Start interview
            fetch('/interview/start', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Save total questions
                    totalQuestions = data.questions.length;
                    currentQuestion = 1;
                    
                    // Update progress
                    updateProgress(currentQuestion, totalQuestions);
                    
                    // Hide setup form, show interview container
                    document.getElementById('interview-setup').style.display = 'none';
                    interviewContainer.style.display = 'block';
                    
                    // Display first question
                    displayQuestion(data.current_question);
                    
                    // Setup audio mode if needed
                    if (interviewMode === 'audio') {
                        setupAudioRecording();
                        document.getElementById('audio-answer-container').style.display = 'block';
                        document.getElementById('text-answer-container').style.display = 'none';
                        
                        // Play question audio
                        getQuestionAudio();
                    } else {
                        document.getElementById('audio-answer-container').style.display = 'none';
                        document.getElementById('text-answer-container').style.display = 'block';
                    }
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
            })
            .finally(() => {
                // Restore button state
                startInterviewBtn.disabled = false;
                startInterviewBtn.innerHTML = 'Start Interview';
            });
        });
    }
    
    // Submit text answer
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    if (submitAnswerBtn) {
        submitAnswerBtn.addEventListener('click', function() {
            const textAnswer = document.getElementById('text-answer').value.trim();
            
            if (!textAnswer) {
                showAlert('Please enter your answer.', 'warning');
                return;
            }
            
            // Show loading state
            submitAnswerBtn.disabled = true;
            submitAnswerBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            
            // Submit answer
            const formData = new FormData();
            formData.append('answer', textAnswer);
            
            fetch('/interview/submit-answer', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display feedback
                    displayFeedback(data.feedback);
                    
                    // Update progress
                    updateProgress(data.question_number, data.total_questions);
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
            })
            .finally(() => {
                // Restore button state
                submitAnswerBtn.disabled = false;
                submitAnswerBtn.innerHTML = 'Submit Answer';
            });
        });
    }
    
    // Next question button
    if (nextQuestionBtn) {
        nextQuestionBtn.addEventListener('click', function() {
            // Show loading state
            nextQuestionBtn.disabled = true;
            nextQuestionBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            
            // Clear previous answer and feedback
            document.getElementById('text-answer').value = '';
            feedbackContainer.style.display = 'none';
            
            // Get next question
            fetch('/interview/next-question', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.finished) {
                        // Show finish UI
                        questionContainer.innerHTML = `<div class="alert alert-success">
                            <h4>Interview Complete!</h4>
                            <p>You have completed all questions. Click "Finish Interview" to see your results.</p>
                        </div>`;
                        document.getElementById('answer-controls').style.display = 'none';
                        finishInterviewBtn.style.display = 'block';
                        nextQuestionBtn.style.display = 'none';
                    } else {
                        // Display next question
                        displayQuestion(data.current_question);
                        
                        // Update progress
                        updateProgress(data.question_number, data.total_questions);
                        
                        // Reset UI
                        document.getElementById('answer-controls').style.display = 'block';
                        feedbackContainer.style.display = 'none';
                        
                        // Play question audio if in audio mode
                        if (interviewMode === 'audio') {
                            getQuestionAudio();
                        }
                    }
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
            })
            .finally(() => {
                // Restore button state
                nextQuestionBtn.disabled = false;
                nextQuestionBtn.innerHTML = 'Next Question';
            });
        });
    }
    
    // Finish interview button
    if (finishInterviewBtn) {
        finishInterviewBtn.addEventListener('click', function() {
            // Show loading state
            finishInterviewBtn.disabled = true;
            finishInterviewBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Finishing...';
            
            // Complete interview
            fetch('/interview/complete', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show summary
                    interviewContainer.innerHTML = `
                        <div class="card mb-4">
                            <div class="card-header bg-primary text-white">
                                <h5 class="card-title mb-0">Interview Summary</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Role: ${data.summary.role}</h6>
                                        <p>Mode: ${data.summary.mode}</p>
                                        <p>Questions answered: ${data.summary.questions_answered}/${data.summary.num_questions}</p>
                                        <p>Duration: ${Math.round(data.summary.duration)} minutes</p>
                                    </div>
                                    <div class="col-md-6 text-md-end">
                                        <div class="display-4 fw-bold">${Math.round(data.summary.overall_score)}/10</div>
                                        <p class="text-muted">Overall Score</p>
                                    </div>
                                </div>
                                
                                <hr>
                                
                                <h6>Overall Feedback:</h6>
                                <p>${data.summary.overall_feedback}</p>
                                
                                <div class="row mt-4">
                                    <div class="col-md-6">
                                        <h6>Strengths:</h6>
                                        <ul>
                                            ${data.summary.strengths.map(s => `<li>${s}</li>`).join('') || '<li>No specific strengths identified</li>'}
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Areas for Improvement:</h6>
                                        <ul>
                                            ${data.summary.areas_for_improvement.map(a => `<li>${a}</li>`).join('') || '<li>No specific areas identified</li>'}
                                        </ul>
                                    </div>
                                </div>
                                
                                <div class="mt-4">
                                    <a href="/interview/view/${data.interview_index}" class="btn btn-primary">
                                        View Detailed Results
                                    </a>
                                    <a href="/interview" class="btn btn-outline-secondary ms-2">
                                        Return to Interview Practice
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
            });
        });
    }
    
    // Helper functions
    function displayQuestion(question) {
        if (!questionContainer) return;
        
        questionContainer.innerHTML = `
            <div class="card border-primary mb-4">
                <div class="card-header bg-primary bg-opacity-75 text-white">
                    <h5 class="card-title mb-0">Question ${currentQuestion}</h5>
                </div>
                <div class="card-body">
                    <p class="fs-5 mb-0">${question}</p>
                </div>
            </div>
        `;
    }
    
    function displayFeedback(feedback) {
        if (!feedbackContainer) return;
        
        let feedbackContent = `
            <div class="card border-info mb-4">
                <div class="card-header bg-info bg-opacity-25">
                    <h5 class="card-title mb-0">Feedback</h5>
                </div>
                <div class="card-body">
                    <p>${feedback.feedback}</p>
                    
                    <div class="row mt-3">
                        <div class="col-md-4">
                            <h6>Clarity</h6>
                            <div class="feedback-meter">
                                <div class="feedback-value bg-primary" style="width: ${feedback.clarity * 10}%"></div>
                            </div>
                            <span class="text-muted">${feedback.clarity}/10</span>
                        </div>
                        <div class="col-md-4">
                            <h6>Relevance</h6>
                            <div class="feedback-meter">
                                <div class="feedback-value bg-success" style="width: ${feedback.relevance * 10}%"></div>
                            </div>
                            <span class="text-muted">${feedback.relevance}/10</span>
                        </div>
                        <div class="col-md-4">
                            <h6>Confidence</h6>
                            <div class="feedback-meter">
                                <div class="feedback-value bg-info" style="width: ${feedback.confidence * 10}%"></div>
                            </div>
                            <span class="text-muted">${feedback.confidence}/10</span>
                        </div>
                    </div>
        `;
        
        // Add speech analysis if available
        if (feedback.speech_analysis) {
            feedbackContent += `
                <hr>
                <h6>Speech Analysis</h6>
                <div class="row">
                    <div class="col-md-6">
                        <p>Word count: ${feedback.speech_analysis.word_count}</p>
                        <p>Fluency score: ${feedback.speech_analysis.fluency_score}/10</p>
                    </div>
                    <div class="col-md-6">
                        <p>Duration: ${Math.round(feedback.speech_analysis.estimated_duration)} seconds</p>
                        <p>${feedback.speech_analysis.feedback}</p>
                    </div>
                </div>
            `;
        }
        
        // Add improvement tips
        if (feedback.improvement_tips && feedback.improvement_tips.length > 0) {
            feedbackContent += `
                <hr>
                <h6>Improvement Tips</h6>
                <ul>
                    ${feedback.improvement_tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            `;
        }
        
        feedbackContent += `
                </div>
            </div>
        `;
        
        feedbackContainer.innerHTML = feedbackContent;
        feedbackContainer.style.display = 'block';
        
        // Show next button
        nextQuestionBtn.style.display = 'block';
    }
    
    function updateProgress(current, total) {
        if (!progressIndicator || !currentQuestionSpan || !totalQuestionsSpan) return;
        
        // Update text indicators
        currentQuestionSpan.textContent = current;
        totalQuestionsSpan.textContent = total;
        
        // Update progress bar
        const percentage = (current / total) * 100;
        progressIndicator.style.width = `${percentage}%`;
        progressIndicator.setAttribute('aria-valuenow', current);
        progressIndicator.setAttribute('aria-valuemax', total);
        
        // Update current question counter
        currentQuestion = current;
    }
    
    function getQuestionAudio() {
        // Request audio version of the question
        fetch('/interview/get-question-audio')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.audio_data) {
                    // Create and play audio
                    const audioElem = document.getElementById('question-audio');
                    if (audioElem) {
                        audioElem.src = `data:audio/mp3;base64,${data.audio_data}`;
                        audioElem.play();
                    }
                }
            })
            .catch(error => {
                console.error('Error getting question audio:', error);
            });
    }
    
    // Interview history interaction
    const viewDetailsButtons = document.querySelectorAll('.view-interview-details');
    if (viewDetailsButtons.length > 0) {
        viewDetailsButtons.forEach(button => {
            button.addEventListener('click', function() {
                const interviewId = this.getAttribute('data-interview-id');
                const detailsContainer = document.getElementById(`interview-details-${interviewId}`);
                
                if (detailsContainer) {
                    // Toggle display
                    if (detailsContainer.style.display === 'none') {
                        detailsContainer.style.display = 'block';
                        this.textContent = 'Hide Details';
                    } else {
                        detailsContainer.style.display = 'none';
                        this.textContent = 'View Details';
                    }
                }
            });
        });
    }
});
