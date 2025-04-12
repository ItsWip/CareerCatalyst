// Resume generator functionality

document.addEventListener('DOMContentLoaded', function() {
    // Job description analysis
    const analyzeBtn = document.getElementById('analyze-job-btn');
    const jobDescTextarea = document.getElementById('job_description');
    const keywordsContainer = document.getElementById('job-keywords');
    const suggestionsContainer = document.getElementById('job-suggestions');
    const matchScoreContainer = document.getElementById('match-score-container');
    
    if (analyzeBtn && jobDescTextarea) {
        analyzeBtn.addEventListener('click', function() {
            const jobDescription = jobDescTextarea.value.trim();
            if (!jobDescription) {
                showAlert('Please enter a job description to analyze.', 'warning');
                return;
            }
            
            // Show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
            keywordsContainer.innerHTML = '<div class="text-center"><div class="loading-spinner"></div><p>Extracting keywords...</p></div>';
            
            // Submit for analysis
            const formData = new FormData();
            formData.append('job_description', jobDescription);
            
            fetch('/resume/analyze-job', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display keywords
                    if (keywordsContainer) {
                        keywordsContainer.innerHTML = '';
                        if (data.keywords && data.keywords.length > 0) {
                            data.keywords.forEach(keyword => {
                                const badge = document.createElement('span');
                                badge.className = 'badge bg-primary me-2 mb-2';
                                badge.textContent = keyword;
                                keywordsContainer.appendChild(badge);
                            });
                        } else {
                            keywordsContainer.innerHTML = '<p class="text-muted">No keywords extracted. Try adding more details to the job description.</p>';
                        }
                    }
                    
                    // Display suggestions
                    if (suggestionsContainer && data.suggestions) {
                        suggestionsContainer.innerHTML = '';
                        
                        // Missing keywords section
                        if (data.suggestions.missing_keywords && data.suggestions.missing_keywords.length > 0) {
                            const missingSection = document.createElement('div');
                            missingSection.className = 'mb-3';
                            missingSection.innerHTML = `
                                <h6>Keywords missing from your profile:</h6>
                                <div class="mb-2">
                                    ${data.suggestions.missing_keywords.map(kw => `<span class="badge bg-warning text-dark me-2 mb-2">${kw}</span>`).join('')}
                                </div>
                            `;
                            suggestionsContainer.appendChild(missingSection);
                        }
                        
                        // Recommendations section
                        if (data.suggestions.recommendations && data.suggestions.recommendations.length > 0) {
                            const recomSection = document.createElement('div');
                            recomSection.innerHTML = `
                                <h6>Recommendations to improve your match:</h6>
                                <ul class="ps-3">
                                    ${data.suggestions.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            `;
                            suggestionsContainer.appendChild(recomSection);
                        }
                        
                        if (!data.suggestions.missing_keywords?.length && !data.suggestions.recommendations?.length) {
                            suggestionsContainer.innerHTML = '<p class="text-success">Great! Your profile already matches most of the job requirements.</p>';
                        }
                    }
                    
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error analyzing job description: ${error}`, 'danger');
            })
            .finally(() => {
                // Restore button state
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = 'Analyze Job Description';
            });
        });
    }
    
    // Template preview functionality
    const templateRadios = document.querySelectorAll('input[name="template"]');
    const templatePreview = document.getElementById('template-preview');
    
    if (templateRadios.length > 0 && templatePreview) {
        templateRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const template = this.value;
                // Update preview image based on selected template
                templatePreview.src = `/static/img/templates/${template}-preview.svg`;
                templatePreview.alt = `${template} template preview`;
            });
        });
    }
    
    // Resume form validation
    const resumeForm = document.getElementById('resume-generator-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function(e) {
            const jobTitle = document.getElementById('job_title').value.trim();
            const jobDescription = document.getElementById('job_description').value.trim();
            
            if (!jobTitle) {
                e.preventDefault();
                showAlert('Please enter a job title.', 'warning');
                document.getElementById('job_title').focus();
                return false;
            }
            
            if (!jobDescription) {
                e.preventDefault();
                showAlert('Please enter a job description.', 'warning');
                document.getElementById('job_description').focus();
                return false;
            }
            
            // Show loading modal
            const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
            loadingModal.show();
            
            return true;
        });
    }
});

// Function to update match score display
function updateMatchScore(score) {
    const matchScoreContainer = document.getElementById('match-score-container');
    if (!matchScoreContainer) return;
    
    // Determine color based on score
    let colorClass = 'bg-danger';
    if (score >= 75) {
        colorClass = 'bg-success';
    } else if (score >= 50) {
        colorClass = 'bg-warning';
    } else if (score >= 30) {
        colorClass = 'bg-info';
    }
    
    // Create match score display
    matchScoreContainer.innerHTML = `
        <div class="match-score ${colorClass} text-white">
            ${Math.round(score)}%
        </div>
        <div class="mt-2 text-center">
            <small>Match Score</small>
        </div>
    `;
}
