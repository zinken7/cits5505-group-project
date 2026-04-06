class Card {
    constructor(element) {
        this.$el = $(element);
        this.$header = this.$el.find('.card-header');
        this.$body = this.$el.find('.card-body');
        this.$toggleIcon = this.$el.find('.card-toggle-icon');
        
        this.isCollapsed = this.$el.hasClass('is-collapsed');
        this.init();
    }

    init() {
        // Ensure card has relative positioning for the loading overlay
        if (!this.$el.hasClass('relative')) {
            this.$el.addClass('relative');
        }

        // Setup collapsible logic if header is clickable
        if (this.$header.hasClass('cursor-pointer')) {
            this.$header.on('click', () => this.toggle());
        }

        // Initial state
        if (this.isCollapsed) {
            this.$body.hide();
            this.$toggleIcon.addClass('rotate-180');
        }
    }

    toggle() {
        this.isCollapsed = !this.isCollapsed;
        if (this.isCollapsed) {
            this.$body.slideUp(200);
            this.$toggleIcon.addClass('rotate-180');
        } else {
            this.$body.slideDown(200);
            this.$toggleIcon.removeClass('rotate-180');
        }
    }

    /**
     * Shows or hides a loading overlay over the entire card
     * @param {boolean} isLoading 
     */
    setLoading(isLoading) {
        let $overlay = this.$el.find('.card-overlay');
        
        if (isLoading) {
            if ($overlay.length === 0) {
                const html = `
                    <div class="card-overlay absolute inset-0 bg-white/60 backdrop-blur-[1px] z-10 flex items-center justify-center rounded-lg">
                        <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>`;
                this.$el.append(html);
            } else {
                $overlay.removeClass('hidden');
            }
        } else {
            if ($overlay.length) {
                $overlay.addClass('hidden');
            }
        }
    }
}

window.UI.card = Card;