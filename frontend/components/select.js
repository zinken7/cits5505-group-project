class Select {
    constructor(element) {
        this.$el = $(element);
        this.$hiddenInput = this.$el.find('input[type="hidden"]');
        this.$trigger = this.$el.find('.select-trigger');
        this.$triggerText = this.$el.find('.select-text');
        this.$menu = this.$el.find('.select-menu');
        this.$options = this.$el.find('.select-option');
        
        this.isOpen = false;
        this.init();
    }

    init() {
        // Toggle menu
        this.$trigger.on('click', (e) => {
            e.preventDefault();
            this.toggle();
        });

        // Select an option
        this.$options.on('click', (e) => {
            const $selected = $(e.currentTarget);
            const val = $selected.data('value');
            const text = $selected.text();

            // Update UI & Hidden Input
            this.$triggerText.text(text).removeClass('text-gray-400').addClass('text-gray-900');
            this.$hiddenInput.val(val).trigger('change');
            
            // Handle active styling
            this.$options.removeClass('bg-blue-50 text-blue-600 font-medium');
            $selected.addClass('bg-blue-50 text-blue-600 font-medium');

            this.close();
        });

        // Close when clicking outside
        $(document).on('click', (e) => {
            if (this.isOpen && !this.$el.is(e.target) && this.$el.has(e.target).length === 0) {
                this.close();
            }
        });
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        this.$menu.removeClass('hidden').hide().fadeIn(150);
        this.$trigger.addClass('border-blue-500 ring-1 ring-blue-500');
        this.isOpen = true;
    }

    close() {
        this.$menu.fadeOut(100, () => this.$menu.addClass('hidden').css('display', ''));
        this.$trigger.removeClass('border-blue-500 ring-1 ring-blue-500');
        this.isOpen = false;
    }
}

window.UI.select = Select;