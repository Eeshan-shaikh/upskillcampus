// Helper functions for working with modals
document.addEventListener('DOMContentLoaded', function() {
    // Initialize modal functionality
    initModals();
    
    function initModals() {
        // Add active class to show modals
        const modals = document.querySelectorAll('.modal');
        
        // Close modal buttons
        const closeButtons = document.querySelectorAll('.close-modal');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const modal = this.closest('.modal');
                closeModal(modal);
            });
        });
        
        // Close when clicking outside of modal content
        modals.forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModal(this);
                }
            });
        });
    }
    
    // Global functions for opening and closing modals
    window.openModal = function(modal) {
        if (modal) {
            modal.classList.add('active');
        }
    };
    
    window.closeModal = function(modal) {
        if (modal) {
            modal.classList.remove('active');
        }
    };
});