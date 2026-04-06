class Popover {
    constructor(element) {
        this.$el = $(element);
        this.$trigger = this.$el.find('.popover-trigger');
        this.$panel = this.$el.find('.popover-panel');
        this.isOpen = false;
        this.init();
    }

    init() {
        this.$trigger.on('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggle();
        });

        // Close on outside click
        $(document).on('click', (e) => {
            if (this.isOpen && !this.$el.is(e.target) && this.$el.has(e.target).length === 0) {
                this.close();
            }
        });
        
        // Prevent clicking inside panel from closing it
        this.$panel.on('click', (e) => {
            e.stopPropagation();
        });
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        // Tailwind transition classes
        this.$panel.removeClass('hidden opacity-0 scale-95').addClass('opacity-100 scale-100');
        this.isOpen = true;
    }

    close() {
        this.$panel.removeClass('opacity-100 scale-100').addClass('opacity-0 scale-95');
        // Hide completely after fade out animation (duration-150)
        setTimeout(() => {
            if (!this.isOpen) this.$panel.addClass('hidden');
        }, 150);
        this.isOpen = false;
    }
}

window.UI.popover = Popover;