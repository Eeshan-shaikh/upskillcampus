document.addEventListener('DOMContentLoaded', function() {
    // Flash message close button
    const closeButtons = document.querySelectorAll('.flash-message .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.parentElement;
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 300);
        });
    }, 5000);
});