// QRWeaver JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize form interactions
    initializeForms();

    // Initialize platform-specific features
    initializePlatformFeatures();

    // Auto-hide flash messages
    initializeFlashMessages();

    // Add smooth scrolling
    initializeSmoothScrolling();
}

function initializeForms() {
    // Form validation and enhancements
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Basic validation
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    highlightInvalidField(field);
                } else {
                    clearInvalidField(field);
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Моля, попълнете всички задължителни полета!', 'error');
            }
        });
    });

    // Real-time URL validation
    const urlInputs = document.querySelectorAll('input[type="url"], input[name="profile_url"]');
    urlInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateSocialUrl(this);
        });
    });
}

function initializePlatformFeatures() {
    // Platform-specific enhancements
    const platform = getCurrentPlatform();

    switch(platform) {
        case 'facebook':
            enhanceFacebookForm();
            break;
        case 'instagram':
            enhanceInstagramForm();
            break;
        case 'linkedin':
            enhanceLinkedInForm();
            break;
    }
}

function getCurrentPlatform() {
    const path = window.location.pathname;
    if (path.includes('facebook')) return 'facebook';
    if (path.includes('instagram')) return 'instagram';
    if (path.includes('linkedin')) return 'linkedin';
    return 'home';
}

function enhanceFacebookForm() {
    // Facebook-specific enhancements
    const profileInput = document.getElementById('profile_url');
    if (profileInput) {
        profileInput.addEventListener('input', function() {
            // Auto-format Facebook URLs
            const value = this.value.trim();
            if (value && !value.includes('facebook.com') && !value.startsWith('http')) {
                this.value = `https://facebook.com/${value.replace('@', '')}`;
            }
        });
    }
}

function enhanceInstagramForm() {
    // Instagram-specific enhancements
    const profileInput = document.getElementById('profile_url');
    const displayInput = document.getElementById('display_name');

    if (profileInput && displayInput) {
        profileInput.addEventListener('input', function() {
            const value = this.value.trim();

            // Auto-fill display name with @username
            if (value && !value.includes('@') && displayInput.value === '') {
                const username = value.replace('instagram.com/', '').replace('/', '');
                displayInput.value = `@${username}`;
            }

            // Auto-format Instagram URLs
            if (value && !value.includes('instagram.com') && !value.startsWith('http')) {
                this.value = `https://instagram.com/${value.replace('@', '')}`;
            }
        });
    }
}

function enhanceLinkedInForm() {
    // LinkedIn-specific enhancements
    const profileInput = document.getElementById('profile_url');
    if (profileInput) {
        profileInput.addEventListener('input', function() {
            // Auto-format LinkedIn URLs
            const value = this.value.trim();
            if (value && !value.includes('linkedin.com') && !value.startsWith('http')) {
                this.value = `https://linkedin.com/in/${value}`;
            }
        });
    }
}

function validateSocialUrl(input) {
    const value = input.value.trim();
    if (!value) return;

    const platform = getCurrentPlatform();
    let isValid = true;
    let message = '';

    switch(platform) {
        case 'facebook':
            isValid = /(facebook\.com|fb\.com)/i.test(value) || !value.includes('.');
            message = isValid ? '' : 'Моля, въведете валиден Facebook профил';
            break;
        case 'instagram':
            isValid = /(instagram\.com|@)/i.test(value) || !value.includes('.');
            message = isValid ? '' : 'Моля, въведете валиден Instagram профил';
            break;
        case 'linkedin':
            isValid = /linkedin\.com\/in/i.test(value) || !value.includes('.');
            message = isValid ? '' : 'Моля, въведете валиден LinkedIn профил';
            break;
    }

    if (!isValid) {
        highlightInvalidField(input, message);
    } else {
        clearInvalidField(input);
    }
}

function highlightInvalidField(field, message = 'Това поле е задължително') {
    field.style.borderColor = '#F56565';
    field.style.boxShadow = '0 0 0 3px rgba(245, 101, 101, 0.1)';

    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }

    // Add error message
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.style.color = '#F56565';
    errorElement.style.fontSize = '0.9rem';
    errorElement.style.marginTop = '0.5rem';
    errorElement.textContent = message;

    field.parentNode.appendChild(errorElement);
}

function clearInvalidField(field) {
    field.style.borderColor = '';
    field.style.boxShadow = '';

    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
}

function initializeSmoothScrolling() {
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

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// QR Code utilities
function downloadQR(platform) {
    const form = document.querySelector('.download-form');
    if (form) {
        form.submit();
    }
}

function shareQR() {
    const qrImage = document.querySelector('.qr-image');
    const shortlink = document.querySelector('.shortlink')?.textContent;

    if (navigator.share && qrImage) {
        // Convert base64 image to blob for sharing
        fetch(qrImage.src)
            .then(res => res.blob())
            .then(blob => {
                const file = new File([blob], 'qr_code.png', { type: 'image/png' });

                navigator.share({
                    title: 'Моят QR код',
                    text: shortlink ? `Сканирай този QR код: ${shortlink}` : 'Сканирай този QR код',
                    files: [file]
                });
            })
            .catch(err => {
                console.error('Error sharing:', err);
                showNotification('Грешка при споделяне. Моля, изтеглете QR кода.', 'error');
            });
    } else {
        showNotification('Функцията за споделяне не се поддържа от вашия браузър.', 'info');
    }
}

// Form auto-save
function initializeAutoSave() {
    const forms = document.querySelectorAll('.qr-form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        const formId = form.id || 'default-form';

        inputs.forEach(input => {
            // Load saved values
            const savedValue = localStorage.getItem(`${formId}-${input.name}`);
            if (savedValue !== null) {
                input.value = savedValue;
            }

            // Save on input
            input.addEventListener('input', function() {
                localStorage.setItem(`${formId}-${this.name}`, this.value);
            });
        });
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAutoSave);
} else {
    initializeAutoSave();
}

// Export functions for global access
window.QRWeaver = {
    showNotification,
    downloadQR,
    shareQR,
    validateSocialUrl
};
