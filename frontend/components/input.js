class Input {
    constructor(element) {
        this.$el = $(element);
        this.$input = this.$el.find('input, textarea');
        this.$errorText = this.$el.find('.error-message');
        this.init();
    }

    init() {
        // Clear error styling dynamically when user starts typing again
        this.$input.on('input', () => {
            if (this.$input.hasClass('border-red-500')) {
                this.clearError();
            }
        });
    }

    /**
     * Display error state based on API response
     * @param {string} message - Validation error message from server
     */
    setError(message) {
        // Update input borders
        this.$input
            .removeClass('border-gray-300 focus:ring-blue-500 focus:border-blue-500')
            .addClass('border-red-500 focus:ring-red-500 focus:border-red-500');
            
        // Render or update error message text
        if (this.$errorText.length) {
            this.$errorText.text(message).removeClass('hidden');
        } else {
            this.$el.append(`<p class="error-message text-sm text-red-500 mt-1">${message}</p>`);
            this.$errorText = this.$el.find('.error-message');
        }
    }

    clearError() {
        this.$input
            .removeClass('border-red-500 focus:ring-red-500 focus:border-red-500')
            .addClass('border-gray-300 focus:ring-blue-500 focus:border-blue-500');
            
        if (this.$errorText.length) {
            this.$errorText.addClass('hidden');
        }
    }
}

window.UI.input = Input;