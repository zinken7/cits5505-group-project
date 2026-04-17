class DatePicker {
    constructor(element) {
        this.$el = $(element);
        this.$input = this.$el.find('input[type="date"]');
        this.init();
    }

    init() {
        this.$el.on('click', () => {
            try {
                this.$input[0].showPicker();
            } catch (e) {
                this.$input.focus();
            }
        });
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
        this.$el.removeClass('border-border').addClass('border-danger ring-1 ring-danger');
    }
}

window.UI.datepicker = DatePicker;
