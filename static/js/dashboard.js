/**
 * Career Development Platform - Dashboard JavaScript
 * Handles dashboard charts and visualizations
 */

// Wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if we're on the dashboard page
    if (document.getElementById('skill-distribution-chart')) {
        initSkillDistributionChart();
    }
    
    if (document.getElementById('application-status-chart')) {
        initApplicationStatusChart();
    }
    
    if (document.getElementById('activity-timeline-chart')) {
        initActivityTimeline();
    }
    
    // Initialize upcoming deadlines
    initUpcomingDeadlines();
});

/**
 * Initialize the skill distribution chart
 */
function initSkillDistributionChart() {
    const ctx = document.getElementById('skill-distribution-chart').getContext('2d');
    
    // Get skill category data from the data attribute
    const chartContainer = document.getElementById('skill-distribution-chart');
    const skillCategoriesData = JSON.parse(chartContainer.getAttribute('data-categories') || '{}');
    
    // Prepare data for chart
    const categories = Object.keys(skillCategoriesData);
    const counts = Object.values(skillCategoriesData);
    
    // Generate colors based on the number of categories
    const colors = generateChartColors(categories.length);
    
    // Create the chart
    const skillChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: counts,
                backgroundColor: colors,
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
                        color: '#e9ecef'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#495057',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Initialize the application status chart
 */
function initApplicationStatusChart() {
    const ctx = document.getElementById('application-status-chart').getContext('2d');
    
    // Get application status data from the data attribute
    const chartContainer = document.getElementById('application-status-chart');
    const jobApplicationsData = JSON.parse(chartContainer.getAttribute('data-applications') || '{"applied": 0, "saved": 0}');
    
    // Create the chart
    const applicationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jobs'],
            datasets: [
                {
                    label: 'Applied',
                    data: [jobApplicationsData.applied],
                    backgroundColor: '#28a745',
                    borderColor: '#28a745',
                    borderWidth: 1
                },
                {
                    label: 'Saved',
                    data: [jobApplicationsData.saved],
                    backgroundColor: '#007bff',
                    borderColor: '#007bff',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#e9ecef'
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#e9ecef'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#e9ecef'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#495057',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Initialize the activity timeline
 */
function initActivityTimeline() {
    const ctx = document.getElementById('activity-timeline-chart').getContext('2d');
    
    // Get activity data from the data attribute
    const chartContainer = document.getElementById('activity-timeline-chart');
    const activityData = JSON.parse(chartContainer.getAttribute('data-activities') || '[]');
    
    // Prepare data for chart
    const labels = [];
    const resumeData = [];
    const interviewData = [];
    
    // Get the last 7 days for the timeline
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(today.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Initialize counters for this day
        resumeData.push(0);
        interviewData.push(0);
    }
    
    // Count activities for each day
    activityData.forEach(activity => {
        const activityDate = new Date(activity.date);
        const dayDiff = Math.floor((today - activityDate) / (1000 * 60 * 60 * 24));
        
        if (dayDiff >= 0 && dayDiff < 7) {
            const index = 6 - dayDiff;
            
            if (activity.type === 'resume') {
                resumeData[index]++;
            } else if (activity.type === 'interview') {
                interviewData[index]++;
            }
        }
    });
    
    // Create the chart
    const activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Resumes',
                    data: resumeData,
                    borderColor: '#20c997',
                    backgroundColor: 'rgba(32, 201, 151, 0.2)',
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Interviews',
                    data: interviewData,
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.2)',
                    tension: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#e9ecef'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#e9ecef',
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#e9ecef'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#495057',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Generate an array of colors for charts
 * @param {number} count - Number of colors needed
 * @returns {string[]} Array of color strings
 */
function generateChartColors(count) {
    // Predefined colors for common categories
    const colors = [
        '#20c997', // teal
        '#fd7e14', // orange
        '#6f42c1', // purple
        '#0dcaf0', // cyan
        '#d63384', // pink
        '#198754', // green
        '#ffc107', // yellow
        '#0d6efd', // blue
        '#dc3545', // red
        '#6c757d'  // gray
    ];
    
    // If we need more colors than predefined, generate them
    if (count > colors.length) {
        for (let i = colors.length; i < count; i++) {
            // Generate a random color
            const r = Math.floor(Math.random() * 256);
            const g = Math.floor(Math.random() * 256);
            const b = Math.floor(Math.random() * 256);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.8)`);
        }
    }
    
    return colors.slice(0, count);
}

/**
 * Initialize upcoming deadlines functionality
 */
function initUpcomingDeadlines() {
    // Add event listeners for deadline notifications
    const notificationButtons = document.querySelectorAll('.set-reminder-btn');
    
    notificationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const deadline = this.getAttribute('data-deadline');
            const title = this.getAttribute('data-title');
            
            // Check if the browser supports notifications
            if (!("Notification" in window)) {
                alert("This browser does not support desktop notifications");
            } else if (Notification.permission === "granted") {
                // If permission is already granted, set the reminder
                setDeadlineReminder(deadline, title);
            } else if (Notification.permission !== "denied") {
                // Request permission if not already denied
                Notification.requestPermission().then(function (permission) {
                    if (permission === "granted") {
                        setDeadlineReminder(deadline, title);
                    }
                });
            }
        });
    });
}

/**
 * Set a reminder for a deadline
 * @param {string} deadlineStr - Deadline date string
 * @param {string} title - Title of the event
 */
function setDeadlineReminder(deadlineStr, title) {
    const deadline = new Date(deadlineStr);
    const now = new Date();
    
    // If deadline is in the past, don't set a reminder
    if (deadline < now) {
        alert('This deadline has already passed');
        return;
    }
    
    // Calculate time until the deadline (1 day before)
    const reminderDate = new Date(deadline);
    reminderDate.setDate(reminderDate.getDate() - 1);
    
    // If the reminder date is in the past, set it to 1 hour from now
    if (reminderDate < now) {
        reminderDate.setTime(now.getTime() + (1 * 60 * 60 * 1000));
    }
    
    // Store the reminder in localStorage
    const reminders = JSON.parse(localStorage.getItem('deadlineReminders') || '[]');
    
    // Check if reminder already exists
    const exists = reminders.some(reminder => 
        reminder.title === title && 
        reminder.deadline === deadlineStr
    );
    
    if (!exists) {
        reminders.push({
            title: title,
            deadline: deadlineStr,
            reminderTime: reminderDate.toISOString()
        });
        
        localStorage.setItem('deadlineReminders', JSON.stringify(reminders));
        
        // Show confirmation
        alert(`Reminder set for ${title} on ${reminderDate.toLocaleString()}`);
        
        // Create a notification now to confirm
        new Notification('Reminder Set', {
            body: `You will be reminded about "${title}" on ${reminderDate.toLocaleString()}`
        });
    } else {
        alert(`A reminder for "${title}" already exists`);
    }
}

/**
 * Check for due reminders
 * Should be called periodically
 */
function checkReminders() {
    const reminders = JSON.parse(localStorage.getItem('deadlineReminders') || '[]');
    const now = new Date();
    
    reminders.forEach((reminder, index) => {
        const reminderTime = new Date(reminder.reminderTime);
        
        if (reminderTime <= now) {
            // Create notification
            new Notification('Deadline Reminder', {
                body: `Your deadline for "${reminder.title}" is approaching (${reminder.deadline})`
            });
            
            // Remove this reminder
            reminders.splice(index, 1);
        }
    });
    
    // Save updated reminders
    localStorage.setItem('deadlineReminders', JSON.stringify(reminders));
}

// Check reminders every minute
setInterval(checkReminders, 60000);
