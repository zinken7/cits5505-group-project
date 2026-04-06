class Avatar {
    constructor(element) {
        this.$el = $(element);
        this.$img = this.$el.find('img');
        this.$fallback = this.$el.find('.avatar-fallback');
        this.init();
    }

    init() {
        if (this.$img.length) {
            this.$img.on('error', () => {
                this.showFallback();
            });

            if (this.$img[0].complete && this.$img[0].naturalHeight === 0) {
                this.showFallback();
            }
        }
    }

    showFallback() {
        this.$img.addClass('hidden');
        
        if (this.$fallback.length) {
            this.$fallback.removeClass('hidden').addClass('flex items-center justify-center');
        } else {
            const defaultIcon = `
                <svg class="w-full h-full text-gray-400 bg-gray-100 p-1 rounded-full" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
            `;
            this.$el.html(defaultIcon);
        }
    }
}

window.UI.avatar = Avatar;