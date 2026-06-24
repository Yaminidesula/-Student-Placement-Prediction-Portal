/**
 * Student Placement Prediction Portal - Main JavaScript
 * Handles UI interactions and form validations
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize flash message auto-dismiss
    initFlashMessages();
    
    // Initialize sidebar toggle for mobile
    initSidebarToggle();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize smooth scrolling
    initSmoothScroll();
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Auto-dismiss flash messages after 5 seconds
 */
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
}

/**
 * Initialize sidebar toggle for mobile devices
 */
function initSidebarToggle() {
    // Check if we're on mobile
    if (window.innerWidth <= 991) {
        // Add mobile menu button if not exists
        if (!document.querySelector('.mobile-menu-btn')) {
            const header = document.querySelector('.main-header .container-fluid');
            const menuBtn = document.createElement('button');
            menuBtn.className = 'mobile-menu-btn btn btn-link text-white';
            menuBtn.innerHTML = '<i class="bi bi-list fs-4"></i>';
            menuBtn.onclick = toggleSidebar;
            
            const col = header.querySelector('.col-md-4');
            if (col) {
                col.prepend(menuBtn);
            }
        }
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        const sidebar = document.querySelector('.sidebar');
        const menuBtn = document.querySelector('.mobile-menu-btn');
        
        if (sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && (!menuBtn || !menuBtn.contains(e.target))) {
                sidebar.classList.remove('show');
            }
        }
    });
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
}

/**
 * Initialize form validations
 */
function initFormValidations() {
    // Add validation styles to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for percentage inputs
    const percentageInputs = document.querySelectorAll('input[type="number"][max="100"]');
    percentageInputs.forEach(input => {
        input.addEventListener('input', function() {
            validatePercentage(this);
        });
    });
}

/**
 * Validate percentage input
 */
function validatePercentage(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min) || 0;
    const max = parseFloat(input.max) || 100;
    
    if (value < min || value > max) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        return true;
    }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Toggle password visibility
 * @param {string} inputId - ID of password input
 * @param {string} iconId - ID of toggle icon
 */
function togglePassword(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = document.getElementById(iconId);
    
    if (passwordInput && toggleIcon) {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.classList.remove('bi-eye');
            toggleIcon.classList.add('bi-eye-slash');
        } else {
            passwordInput.type = 'password';
            toggleIcon.classList.remove('bi-eye-slash');
            toggleIcon.classList.add('bi-eye');
        }
    }
}

/**
 * Confirm action before proceeding
 * @param {string} message - Confirmation message
 * @returns {boolean} - True if confirmed, false otherwise
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

/**
 * Show loading spinner
 * @param {HTMLElement} element - Element to show spinner in
 */
function showLoading(element) {
    if (element) {
        element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        element.disabled = true;
    }
}

/**
 * Hide loading spinner and restore button text
 * @param {HTMLElement} element - Element to hide spinner from
 * @param {string} originalText - Original button text
 */
function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

/**
 * Format date for display
 * @param {string} dateString - Date string to format
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Animate number counting
 * @param {HTMLElement} element - Element to animate
 * @param {number} target - Target number
 * @param {number} duration - Animation duration in ms
 */
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

/**
 * Handle window resize
 */
window.addEventListener('resize', function() {
    const sidebar = document.querySelector('.sidebar');
    
    if (window.innerWidth > 991) {
        // Remove show class on desktop
        if (sidebar) {
            sidebar.classList.remove('show');
        }
    }
});

// Export functions for global access
window.togglePassword = togglePassword;
window.confirmAction = confirmAction;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatDate = formatDate;
window.animateNumber = animateNumber;
window.toggleSidebar = toggleSidebar;
