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
            if (this.$input.hasClass('border-danger')) {
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
            .removeClass('border-border focus:ring-primary focus:border-primary')
            .addClass('border-danger focus:ring-danger focus:border-danger');

        // Render or update error message text
        if (this.$errorText.length) {
            this.$errorText.text(message).removeClass('hidden');
        } else {
            this.$el.append(`<p class="error-message text-sm text-danger mt-1">${message}</p>`);
            this.$errorText = this.$el.find('.error-message');
        }
    }

    clearError() {
        this.$input
            .removeClass('border-danger focus:ring-danger focus:border-danger')
            .addClass('border-border focus:ring-primary focus:border-primary');
            
        if (this.$errorText.length) {
            this.$errorText.addClass('hidden');
        }
    }
}

window.UI.input = Input;