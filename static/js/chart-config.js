// Chart configurations for dashboard

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Profile completeness chart
    const completenessCanvas = document.getElementById('completenessChart');
    if (completenessCanvas) {
        const completeness = parseFloat(completenessCanvas.getAttribute('data-completeness') || 0);
        
        new Chart(completenessCanvas, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [completeness, 100 - completeness],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(108, 117, 125, 0.2)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '75%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed}% complete`;
                            }
                        }
                    }
                }
            }
        });
        
        // Add center text
        const completenessText = document.getElementById('completenessText');
        if (completenessText) {
            completenessText.textContent = `${Math.round(completeness)}%`;
        }
    }
    
    // Interview performance chart
    const interviewCanvas = document.getElementById('interviewPerformanceChart');
    if (interviewCanvas) {
        const scoresData = JSON.parse(interviewCanvas.getAttribute('data-scores') || '[]');
        const labels = scoresData.map((_, index) => `Interview ${index + 1}`);
        
        new Chart(interviewCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Score',
                    data: scoresData,
                    borderColor: 'rgba(13, 110, 253, 0.8)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Skills breakdown chart
    const skillsCanvas = document.getElementById('skillsBreakdownChart');
    if (skillsCanvas) {
        const skillsData = JSON.parse(skillsCanvas.getAttribute('data-skills') || '[]');
        
        // Sort skills by frequency
        const sortedSkills = skillsData.sort((a, b) => b.count - a.count).slice(0, 8);
        
        new Chart(skillsCanvas, {
            type: 'bar',
            data: {
                labels: sortedSkills.map(skill => skill.name),
                datasets: [{
                    label: 'Demand',
                    data: sortedSkills.map(skill => skill.count),
                    backgroundColor: 'rgba(13, 110, 253, 0.7)',
                    borderWidth: 0
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.x} job postings`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Jobs by type chart
    const jobTypesCanvas = document.getElementById('jobTypesChart');
    if (jobTypesCanvas) {
        const jobTypesData = JSON.parse(jobTypesCanvas.getAttribute('data-job-types') || '{}');
        
        new Chart(jobTypesCanvas, {
            type: 'pie',
            data: {
                labels: Object.keys(jobTypesData),
                datasets: [{
                    data: Object.values(jobTypesData),
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.7)',
                        'rgba(40, 167, 69, 0.7)',
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(255, 193, 7, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12
                        }
                    }
                }
            }
        });
    }
    
    // Resume match scores chart
    const resumeScoresCanvas = document.getElementById('resumeScoresChart');
    if (resumeScoresCanvas) {
        const resumeData = JSON.parse(resumeScoresCanvas.getAttribute('data-resumes') || '[]');
        
        // Sort by date (newest first)
        const sortedResumes = resumeData.sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5);
        
        new Chart(resumeScoresCanvas, {
            type: 'bar',
            data: {
                labels: sortedResumes.map(r => r.job_title),
                datasets: [{
                    label: 'Match Score',
                    data: sortedResumes.map(r => r.score),
                    backgroundColor: sortedResumes.map(r => {
                        if (r.score >= 75) return 'rgba(40, 167, 69, 0.7)';
                        if (r.score >= 50) return 'rgba(255, 193, 7, 0.7)';
                        return 'rgba(220, 53, 69, 0.7)';
                    }),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Match score: ${context.parsed.y}%`;
                            }
                        }
                    }
                }
            }
        });
    }
});
