// QRWeaver JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Example buttons functionality
    const exampleButtons = document.querySelectorAll('.example-btn');
    const qrTextarea = document.getElementById('qr_data');

    exampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exampleText = this.getAttribute('data-example');
            if (qrTextarea) {
                qrTextarea.value = exampleText;

                // Smooth scroll to form
                qrTextarea.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });

                // Focus the textarea
                qrTextarea.focus();
            }
        });
    });

    // Form validation
    const qrForm = document.querySelector('.qr-form');
    if (qrForm) {
        qrForm.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea[name="qr_data"]');
            if (textarea && textarea.value.trim().length === 0) {
                e.preventDefault();
                showNotification('Моля, въведете данни за QR кода!', 'error');
                textarea.focus();
            }
        });
    }

    // Style preview (optional enhancement)
    const styleSelect = document.getElementById('style');
    if (styleSelect) {
        styleSelect.addEventListener('change', function() {
            updateStylePreview(this.value);
        });
    }

    // Flash messages auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
});

function updateStylePreview(style) {
    // This could be enhanced to show style previews
    const colors = {
        'modern': { primary: '#6A5ACD', name: 'Модерен' },
        'vibrant': { primary: '#ED8936', name: 'Енергичен' },
        'professional': { primary: '#2D3748', name: 'Професионален' },
        'creative': { primary: '#48BB78', name: 'Креативен' }
    };

    const styleInfo = colors[style];
    if (styleInfo) {
        console.log(`Избран стил: ${styleInfo.name}`);
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// Service Worker for PWA capabilities (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed: ', error);
            });
    });
}