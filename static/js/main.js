// PG Tutoring Hub - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAnimations();
    initializeFormValidation();
    initializeTooltips();
    initializeCharts();
    initializeNotifications();
});

// Animation Utilities
function initializeAnimations() {
    // Add fade-in animation to cards on page load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Form Validation Enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields correctly.', 'error');
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    let isValid = true;
    let errorMessage = '';

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }

    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }

    // Password validation
    if (fieldType === 'password' && value && value.length < 8) {
        isValid = false;
        errorMessage = 'Password must be at least 8 characters long.';
    }

    // Update field styling
    updateFieldValidation(field, isValid, errorMessage);
    
    return isValid;
}

function updateFieldValidation(field, isValid, errorMessage) {
    const fieldContainer = field.closest('.mb-3') || field.parentNode;
    let errorDiv = fieldContainer.querySelector('.validation-error');

    // Remove existing error styling
    field.classList.remove('is-invalid', 'is-valid');
    
    if (errorDiv) {
        errorDiv.remove();
    }

    if (!isValid && errorMessage) {
        field.classList.add('is-invalid');
        
        // Add error message
        errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error text-danger small mt-1';
        errorDiv.textContent = errorMessage;
        fieldContainer.appendChild(errorDiv);
    } else if (field.value.trim()) {
        field.classList.add('is-valid');
    }
}

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Dashboard Charts (if Chart.js is included)
function initializeCharts() {
    // Progress Chart
    const progressChart = document.getElementById('progressChart');
    if (progressChart && typeof Chart !== 'undefined') {
        const ctx = progressChart.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [65, 20, 15],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'bottom'
                }
            }
        });
    }

    // Activity Chart
    const activityChart = document.getElementById('activityChart');
    if (activityChart && typeof Chart !== 'undefined') {
        const ctx = activityChart.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Study Hours',
                    data: [2, 3, 1, 4, 2, 3, 1],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Notification System
function initializeNotifications() {
    // Auto-hide success messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                fadeOut(alert);
            }, 5000);
        }
    });
}

function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = getOrCreateNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Auto-remove notification
    setTimeout(() => {
        if (notification.parentNode) {
            fadeOut(notification);
        }
    }, duration);
    
    return notification;
}

function getOrCreateNotificationContainer() {
    let container = document.getElementById('notification-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    return container;
}

// Utility Functions
function fadeOut(element, duration = 300) {
    element.style.transition = `opacity ${duration}ms`;
    element.style.opacity = '0';
    
    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, duration);
}

function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms`;
    
    setTimeout(() => {
        element.style.opacity = '1';
    }, 10);
}

// Loading States
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading-spinner"></span> Loading...';
    button.disabled = true;
    button.dataset.originalText = originalText;
}

function hideLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

// File Upload Preview
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const preview = createFilePreview(file);
                const container = this.closest('.mb-3');
                
                // Remove existing preview
                const existingPreview = container.querySelector('.file-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                container.appendChild(preview);
            }
        });
    });
}

function createFilePreview(file) {
    const preview = document.createElement('div');
    preview.className = 'file-preview mt-2 p-2 border rounded';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        img.className = 'img-thumbnail';
        preview.appendChild(img);
    } else {
        preview.innerHTML = `
            <i class="fas fa-file"></i>
            <span class="ms-2">${file.name}</span>
            <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
        `;
    }
    
    return preview;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Search Functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            const query = this.value.toLowerCase();
            const targetSelector = this.dataset.target;
            const items = document.querySelectorAll(targetSelector);
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const matches = text.includes(query);
                item.style.display = matches ? '' : 'none';
            });
        }, 300));
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.PGTutoring = {
    showNotification,
    showLoading,
    hideLoading,
    validateForm,
    fadeIn,
    fadeOut
};