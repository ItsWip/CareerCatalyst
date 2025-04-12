// Main JavaScript for the CareerCompass application

// Initialize tooltips and popovers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Add event listeners for delete buttons
    setupDeleteButtons();
    
    // Setup profile form sections
    setupProfileForms();
    
    // Setup opportunity filtering
    setupOpportunityFilters();
});

// Function to setup delete confirmation modals
function setupDeleteButtons() {
    // Generic delete confirmation
    const deleteModal = document.getElementById('deleteConfirmModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const itemId = button.getAttribute('data-item-id');
            const itemType = button.getAttribute('data-item-type');
            const confirmButton = deleteModal.querySelector('.btn-danger');
            
            deleteModal.querySelector('.modal-body').textContent = `Are you sure you want to delete this ${itemType}?`;
            
            confirmButton.setAttribute('data-item-id', itemId);
            confirmButton.setAttribute('data-item-type', itemType);
        });
        
        // Handle delete confirmation
        const confirmButton = deleteModal.querySelector('.btn-danger');
        if (confirmButton) {
            confirmButton.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const itemType = this.getAttribute('data-item-type');
                
                let url = '';
                if (itemType === 'resume') {
                    url = `/resume/delete/${itemId}`;
                } else if (itemType === 'interview') {
                    url = `/interview/delete/${itemId}`;
                } else if (itemType === 'saved-opportunity') {
                    url = `/opportunities/remove-saved`;
                    // For saved opportunities, the itemId is the URL
                    return fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `url=${encodeURIComponent(itemId)}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Close modal
                            const modalInstance = bootstrap.Modal.getInstance(deleteModal);
                            modalInstance.hide();
                            
                            // Remove the item from the DOM
                            const itemElement = document.querySelector(`[data-url="${itemId}"]`);
                            if (itemElement) {
                                const parentCard = itemElement.closest('.card');
                                if (parentCard) {
                                    parentCard.remove();
                                }
                            }
                            
                            // Show success message
                            showAlert('Item deleted successfully.', 'success');
                        } else {
                            showAlert(`Error: ${data.message}`, 'danger');
                        }
                    })
                    .catch(error => {
                        showAlert(`Error: ${error}`, 'danger');
                    });
                }
                
                // For resume and interview deletes
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Close modal
                        const modalInstance = bootstrap.Modal.getInstance(deleteModal);
                        modalInstance.hide();
                        
                        // Remove the item from the DOM
                        const itemElement = document.querySelector(`[data-item-id="${itemId}"][data-item-type="${itemType}"]`);
                        if (itemElement) {
                            const parentCard = itemElement.closest('.card');
                            if (parentCard) {
                                parentCard.remove();
                            }
                        }
                        
                        // Show success message
                        showAlert('Item deleted successfully.', 'success');
                    } else {
                        showAlert(`Error: ${data.message}`, 'danger');
                    }
                })
                .catch(error => {
                    showAlert(`Error: ${error}`, 'danger');
                });
            });
        }
    }
}

// Function to setup profile form sections
function setupProfileForms() {
    // Education form
    setupAddRemoveSection('education', function(form) {
        return {
            degree: form.querySelector('[name="degree"]').value,
            institution: form.querySelector('[name="institution"]').value,
            location: form.querySelector('[name="location"]').value,
            start_date: form.querySelector('[name="start_date"]').value,
            end_date: form.querySelector('[name="end_date"]').value,
            gpa: form.querySelector('[name="gpa"]').value,
            description: form.querySelector('[name="description"]').value
        };
    });
    
    // Experience form
    setupAddRemoveSection('experience', function(form) {
        return {
            title: form.querySelector('[name="title"]').value,
            company: form.querySelector('[name="company"]').value,
            location: form.querySelector('[name="location"]').value,
            start_date: form.querySelector('[name="start_date"]').value,
            end_date: form.querySelector('[name="end_date"]').value,
            description: form.querySelector('[name="description"]').value,
            responsibilities: form.querySelector('[name="responsibilities"]').value,
            achievements: form.querySelector('[name="achievements"]').value
        };
    });
    
    // Project form
    setupAddRemoveSection('project', function(form) {
        return {
            name: form.querySelector('[name="name"]').value,
            description: form.querySelector('[name="description"]').value,
            technologies: form.querySelector('[name="technologies"]').value,
            url: form.querySelector('[name="url"]').value,
            start_date: form.querySelector('[name="start_date"]').value,
            end_date: form.querySelector('[name="end_date"]').value
        };
    });
    
    // Certification form
    setupAddRemoveSection('certification', function(form) {
        return {
            name: form.querySelector('[name="name"]').value,
            issuer: form.querySelector('[name="issuer"]').value,
            date: form.querySelector('[name="date"]').value,
            expiry: form.querySelector('[name="expiry"]').value,
            url: form.querySelector('[name="url"]').value
        };
    });
    
    // Achievement form
    setupAddRemoveSection('achievement', function(form) {
        return {
            achievement: form.querySelector('[name="achievement"]').value
        };
    });
}

// Helper function to setup add/remove functionality for profile sections
function setupAddRemoveSection(sectionType, getFormData) {
    const addForm = document.getElementById(`add-${sectionType}-form`);
    if (!addForm) return;
    
    addForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitButton = addForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Get form data
        const formData = getFormData(addForm);
        
        // Convert to form data for submission
        const submitData = new FormData();
        Object.keys(formData).forEach(key => {
            submitData.append(key, formData[key]);
        });
        
        // Submit the form
        fetch(`/profile/${sectionType}/add`, {
            method: 'POST',
            body: submitData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reset form
                addForm.reset();
                
                // Close modal if it exists
                const modalId = `add${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)}Modal`;
                const modal = document.getElementById(modalId);
                if (modal) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
                
                // Show success message
                showAlert(`${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} added successfully.`, 'success');
                
                // Reload the page to show updated data
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showAlert(`Error: ${data.message}`, 'danger');
            }
        })
        .catch(error => {
            showAlert(`Error: ${error}`, 'danger');
        })
        .finally(() => {
            // Restore button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        });
    });
    
    // Setup remove buttons
    document.querySelectorAll(`.remove-${sectionType}-btn`).forEach(button => {
        button.addEventListener('click', function() {
            const index = this.getAttribute('data-index');
            
            // Show loading state
            const originalButtonText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            
            fetch(`/profile/${sectionType}/remove/${index}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove element from DOM
                    const itemElement = this.closest(`.${sectionType}-item`);
                    if (itemElement) {
                        itemElement.remove();
                    }
                    
                    // Show success message
                    showAlert(`${sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} removed successfully.`, 'success');
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
            })
            .finally(() => {
                // Restore button state
                this.disabled = false;
                this.innerHTML = originalButtonText;
            });
        });
    });
}

// Function to setup opportunity filters
function setupOpportunityFilters() {
    const jobFilterForm = document.getElementById('job-filter-form');
    const hackathonFilterForm = document.getElementById('hackathon-filter-form');
    
    if (jobFilterForm) {
        jobFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get filter values
            const keywords = jobFilterForm.querySelector('[name="keywords"]').value;
            const jobType = jobFilterForm.querySelector('[name="job_type"]').value;
            const location = jobFilterForm.querySelector('[name="location"]').value;
            const useProfile = jobFilterForm.querySelector('[name="use_profile"]').checked ? '1' : '0';
            
            // Build URL with query parameters
            let url = `/opportunities/jobs?keywords=${encodeURIComponent(keywords)}&job_type=${encodeURIComponent(jobType)}&location=${encodeURIComponent(location)}&use_profile=${useProfile}`;
            
            // Navigate to filtered results
            window.location.href = url;
        });
    }
    
    if (hackathonFilterForm) {
        hackathonFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get filter values
            const keywords = hackathonFilterForm.querySelector('[name="keywords"]').value;
            const location = hackathonFilterForm.querySelector('[name="location"]').value;
            const remote = hackathonFilterForm.querySelector('[name="remote"]').value;
            const skillLevel = hackathonFilterForm.querySelector('[name="skill_level"]').value;
            const teamSize = hackathonFilterForm.querySelector('[name="team_size"]').value;
            
            // Build URL with query parameters
            let url = `/opportunities/hackathons?keywords=${encodeURIComponent(keywords)}&location=${encodeURIComponent(location)}&remote=${encodeURIComponent(remote)}&skill_level=${encodeURIComponent(skillLevel)}&team_size=${encodeURIComponent(teamSize)}`;
            
            // Navigate to filtered results
            window.location.href = url;
        });
    }
    
    // Setup save buttons for jobs and hackathons
    document.querySelectorAll('.save-job-btn').forEach(button => {
        button.addEventListener('click', function() {
            const jobId = this.getAttribute('data-job-id');
            
            // Show loading state
            const originalButtonText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            
            const formData = new FormData();
            formData.append('job_id', jobId);
            
            fetch('/opportunities/save-job', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update button
                    this.innerHTML = '<i class="fas fa-check"></i> Saved';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                    
                    // Show success message
                    showAlert('Job saved successfully.', 'success');
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                    this.innerHTML = originalButtonText;
                    this.disabled = false;
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
                this.innerHTML = originalButtonText;
                this.disabled = false;
            });
        });
    });
    
    document.querySelectorAll('.save-hackathon-btn').forEach(button => {
        button.addEventListener('click', function() {
            const hackathonId = this.getAttribute('data-hackathon-id');
            
            // Show loading state
            const originalButtonText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            
            const formData = new FormData();
            formData.append('hackathon_id', hackathonId);
            
            fetch('/opportunities/save-hackathon', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update button
                    this.innerHTML = '<i class="fas fa-check"></i> Saved';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                    
                    // Show success message
                    showAlert('Hackathon saved successfully.', 'success');
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                    this.innerHTML = originalButtonText;
                    this.disabled = false;
                }
            })
            .catch(error => {
                showAlert(`Error: ${error}`, 'danger');
                this.innerHTML = originalButtonText;
                this.disabled = false;
            });
        });
    });
}

// Helper function to display alerts
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) {
        console.error('Alerts container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertInstance = new bootstrap.Alert(alertDiv);
        alertInstance.close();
    }, 5000);
}
