class Pagination {
    constructor(element) {
        this.$el = $(element);
        this.init();
    }

    init() {
        this.$el.on('click', '[data-page]', (e) => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            
            if (page === 'prev' || page === 'next') {
                // Logic for prev/next buttons should be handled in your API service
                this.triggerChange(page);
            } else {
                this.setCurrentPage(parseInt(page));
                this.triggerChange(page);
            }
        });
    }

    setCurrentPage(pageNumber) {
        const $nums = this.$el.find('[data-page]').filter(function () {
            const p = $(this).data('page');
            return p !== 'prev' && p !== 'next';
        });

        const inactive =
            'text-foreground ring-1 ring-inset ring-border hover:bg-muted/10 transition-colors';
        const active = 'z-10 bg-primary text-white';

        $nums.removeClass(active).addClass(inactive);

        this.$el
            .find(`[data-page="${pageNumber}"]`)
            .first()
            .removeClass(inactive)
            .addClass(active);
    }

    triggerChange(page) {
        // Custom event so you can listen to it in your page.js
        this.$el.trigger('ui:page-change', { page: page });
    }
}

window.UI.pagination = Pagination;