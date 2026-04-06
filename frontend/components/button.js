class Button {
    constructor(element) {
        this.$el = $(element);
        this.originalContent = this.$el.html();
        this.isLoading = false;
    }

    /**
     * Set the button to a loading state, disabling it and showing a spinner.
     * @param {boolean} state 
     */
    setLoading(state) {
        this.isLoading = state;
        
        if (state) {
            this.$el.prop('disabled', true).addClass('opacity-75 cursor-not-allowed');
            
            const spinner = `
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
            
            this.$el.html(`<div class="flex items-center justify-center">${spinner} <span>${this.originalContent}</span></div>`);
        } else {
            this.$el.prop('disabled', false).removeClass('opacity-75 cursor-not-allowed');
            this.$el.html(this.originalContent);
        }
    }
}

window.UI.button = Button;