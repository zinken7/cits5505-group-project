class Accordion {
    constructor(element) {
        this.$el = $(element);
        // Add data-multiple="true" to HTML if you want multiple panels open at once
        this.allowMultiple = this.$el.data('multiple') === true; 
        this.init();
    }

    init() {
        this.$el.on('click', '.accordion-header', (e) => {
            const $header = $(e.currentTarget);
            const $item = $header.closest('.accordion-item');
            const $content = $item.find('.accordion-content');
            const $icon = $header.find('.accordion-icon');
            
            const isOpen = $item.hasClass('is-open');

            // If not allowing multiple, close all others
            if (!this.allowMultiple && !isOpen) {
                const $otherItems = this.$el.find('.accordion-item.is-open');
                $otherItems.removeClass('is-open');
                $otherItems.find('.accordion-content').slideUp(200);
                $otherItems.find('.accordion-icon').removeClass('rotate-180');
            }

            // Toggle current
            if (isOpen) {
                $item.removeClass('is-open');
                $content.slideUp(200);
                $icon.removeClass('rotate-180');
            } else {
                $item.addClass('is-open');
                $content.slideDown(200);
                $icon.addClass('rotate-180');
            }
        });

        // Initialize state based on HTML classes
        this.$el.find('.accordion-item').each((_, item) => {
            if (!$(item).hasClass('is-open')) {
                $(item).find('.accordion-content').hide();
            } else {
                $(item).find('.accordion-icon').addClass('rotate-180');
            }
        });
    }
}

window.UI.accordion = Accordion;