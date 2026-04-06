class Toggle {
    constructor(element) {
        this.$el = $(element);
        this.$input = this.$el.find('input[type="checkbox"]');
        this.$track = this.$el.find('.toggle-track');
        this.$thumb = this.$el.find('.toggle-thumb');
        this.init();
    }

    init() {
        // Handle click on the wrapper
        this.$el.on('click', (e) => {
            if (this.$input.prop('disabled')) return;
            
            // Prevent double-toggling if they actually clicked the hidden input
            if (e.target !== this.$input[0]) {
                this.$input.prop('checked', !this.$input.prop('checked')).trigger('change');
            }
            this.updateUI();
        });

        // Sync initial state from HTML
        this.updateUI();
    }

    updateUI() {
        const isChecked = this.$input.prop('checked');
        
        if (isChecked) {
            this.$track.removeClass('bg-gray-200').addClass('bg-blue-600');
            this.$thumb.addClass('translate-x-5'); // Move to right
        } else {
            this.$track.removeClass('bg-blue-600').addClass('bg-gray-200');
            this.$thumb.removeClass('translate-x-5'); // Move to left
        }
    }
}

window.UI.toggle = Toggle;