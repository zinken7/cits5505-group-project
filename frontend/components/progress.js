class Progress {
    constructor(element) {
        this.$el = $(element);
        this.$bar = this.$el.find('.progress-bar');
        this.$text = this.$el.find('.progress-text'); // Optional text indicator
        this.init();
    }

    init() {
        // Read initial value from data attribute if exists
        const initialValue = this.$el.data('value') || 0;
        this.setValue(initialValue);
    }

    /**
     * Updates the progress bar width
     * @param {number} percent - Value from 0 to 100
     */
    setValue(percent) {
        // Clamp value between 0 and 100
        const clampedValue = Math.max(0, Math.min(100, percent));
        
        // Update UI
        this.$bar.css('width', `${clampedValue}%`);
        this.$el.data('value', clampedValue);
        
        if (this.$text.length) {
            this.$text.text(`${Math.round(clampedValue)}%`);
        }
    }
}

window.UI.progress = Progress;