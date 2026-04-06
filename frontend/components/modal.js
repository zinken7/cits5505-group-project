class Modal {
    constructor(element) {
        this.$el = $(element);
        this.$backdrop = this.$el.find('.modal-backdrop');
        this.$panel = this.$el.find('.modal-panel');
        this.$closeBtns = this.$el.find('[data-dismiss="modal"]');
        
        this.isOpen = !this.$el.hasClass('hidden');
        this.init();
    }

    init() {
        // Trigger to open modal (find any button with data-target="#this-modal-id")
        const modalId = this.$el.attr('id');
        if (modalId) {
            $(document).on('click', `[data-target="#${modalId}"]`, (e) => {
                e.preventDefault();
                this.open();
            });
        }

        // Close on button click
        this.$closeBtns.on('click', (e) => {
            e.preventDefault();
            this.close();
        });

        // Close on backdrop click
        this.$backdrop.on('click', () => {
            this.close();
        });

        // Close on ESC key press
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    open() {
        if (this.isOpen) return;
        
        // Lock body scroll
        $('body').addClass('overflow-hidden');
        
        // Show modal wrapper
        this.$el.removeClass('hidden');
        
        // Animate in
        setTimeout(() => {
            this.$backdrop.removeClass('opacity-0').addClass('opacity-100');
            this.$panel.removeClass('opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95')
                       .addClass('opacity-100 translate-y-0 sm:scale-100');
        }, 10); // Small delay to allow display:block to apply before animating

        this.isOpen = true;
    }

    close() {
        if (!this.isOpen) return;

        // Animate out
        this.$backdrop.removeClass('opacity-100').addClass('opacity-0');
        this.$panel.removeClass('opacity-100 translate-y-0 sm:scale-100')
                   .addClass('opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95');

        // Hide wrapper and unlock body after animation ends (300ms matches Tailwind duration-300)
        setTimeout(() => {
            this.$el.addClass('hidden');
            $('body').removeClass('overflow-hidden');
        }, 300);

        this.isOpen = false;
    }
}

window.UI.modal = Modal;