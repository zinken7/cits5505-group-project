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
        this.$el.find('[data-page]').removeClass('z-10 bg-blue-600 text-white')
                 .addClass('text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50');
        
        this.$el.find(`[data-page="${pageNumber}"]`)
                 .removeClass('text-gray-900 ring-gray-300')
                 .addClass('z-10 bg-blue-600 text-white');
    }

    triggerChange(page) {
        // Custom event so you can listen to it in your page.js
        this.$el.trigger('ui:page-change', { page: page });
    }
}

window.UI.pagination = Pagination;