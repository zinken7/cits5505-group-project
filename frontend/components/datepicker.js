class DatePicker {
    constructor(element) {
        this.$el = $(element);
        this.$input = this.$el.find('input[type="date"]');
        this.init();
    }

    init() {
        // Automatically open the native date picker when clicking anywhere on the wrapper
        this.$el.on('click', () => {
            try {
                this.$input[0].showPicker(); // Supported in modern browsers
            } catch (e) {
                this.$input.focus(); // Fallback for older browsers
            }
        });

        // Add CSS to hide native calendar icon via JS if not done in CSS
        if (!$('#ui-datepicker-styles').length) {
            $('head').append(`
                <style id="ui-datepicker-styles">
                    /* Hide native calendar icon in webkit */
                    input[type="date"]::-webkit-calendar-picker-indicator {
                        background: transparent;
                        bottom: 0;
                        color: transparent;
                        cursor: pointer;
                        height: auto;
                        left: 0;
                        position: absolute;
                        right: 0;
                        top: 0;
                        width: auto;
                    }
                </style>
            `);
        }
    }

    /**
     * Get the date value in YYYY-MM-DD format suitable for backend API
     * @returns {string}
     */
    getValue() {
        return this.$input.val();
    }

    /**
     * Set the date value
     * @param {string} dateString - Format YYYY-MM-DD
     */
    setValue(dateString) {
        this.$input.val(dateString);
    }
    
    /**
     * Show validation error styling
     */
    setError(message) {
        this.$el.removeClass('border-gray-300').addClass('border-red-500 ring-1 ring-red-500');
        // Optional: you could append an error message element here similarly to input.js
    }
}

window.UI.datepicker = DatePicker;