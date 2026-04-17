class Card {
    constructor(element) {
        this.$el = $(element);
        this.$header = this.$el.find(".card-header");
        this.$body = this.$el.find(".card-body");
        this.$toggleIcon = this.$el.find(".card-toggle-icon");

        this.init();
    }

    init() {
        if (!this.$el.hasClass("relative")) {
            this.$el.addClass("relative");
        }

        if (this.$header.hasClass("cursor-pointer")) {
            this.$header.on("click", () => this.toggle());
        }

        if (this.$el.hasClass("is-collapsed")) {
            this.$toggleIcon.addClass("rotate-180");
        }
    }

    toggle() {
        if (this.$el.hasClass("is-collapsed")) {
            this.$body.slideDown(200, () => {
                this.$el.removeClass("is-collapsed");
            });
            this.$toggleIcon.removeClass("rotate-180");
        } else {
            this.$body.slideUp(200, () => {
                this.$el.addClass("is-collapsed");
            });
            this.$toggleIcon.addClass("rotate-180");
        }
    }

    /**
     * Shows or hides a loading overlay over the entire card
     * @param {boolean} isLoading
     */
    setLoading(isLoading) {
        let $overlay = this.$el.find(".card-overlay");

        if (isLoading) {
            if ($overlay.length === 0) {
                const html = `
                    <div class="card-overlay absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-card/80 backdrop-blur-sm">
                        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>`;
                this.$el.append(html);
            } else {
                $overlay.removeClass("hidden");
            }
        } else if ($overlay.length) {
            $overlay.addClass("hidden");
        }
    }
}

window.UI.card = Card;
