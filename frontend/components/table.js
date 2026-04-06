class Table {
    constructor(element) {
        this.$el = $(element);
        this.$selectAll = this.$el.find('.select-all-checkbox');
        this.$sortHeaders = this.$el.find('th[data-sortable]');
        this.init();
    }

    init() {
        // Handle Select All checkbox
        this.$selectAll.on('change', (e) => {
            const isChecked = $(e.currentTarget).prop('checked');
            // Find all row checkboxes dynamically (useful if rows are injected later via CSR)
            const $rowCheckboxes = this.$el.find('.row-checkbox');
            $rowCheckboxes.prop('checked', isChecked);
            this.updateRowStyles();
        });

        // Handle individual row checkbox (Delegate event for dynamically added rows)
        this.$el.on('change', '.row-checkbox', () => {
            const $rowCheckboxes = this.$el.find('.row-checkbox');
            const total = $rowCheckboxes.length;
            const checked = $rowCheckboxes.filter(':checked').length;
            
            this.$selectAll.prop('checked', total > 0 && total === checked);
            this.updateRowStyles();
        });

        // Handle Sortable Headers
        this.$sortHeaders.on('click', (e) => {
            const $header = $(e.currentTarget);
            const column = $header.data('sortable');
            const currentDirection = $header.data('direction') || 'none';
            
            // Determine next direction (none -> asc -> desc -> asc)
            let nextDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Reset UI for all headers
            this.$sortHeaders.data('direction', 'none');
            this.$sortHeaders.find('.sort-icon')
                .removeClass('text-blue-600 rotate-180')
                .addClass('text-gray-400 opacity-0 group-hover:opacity-100');

            // Apply UI to clicked header
            $header.data('direction', nextDirection);
            const $icon = $header.find('.sort-icon');
            $icon.removeClass('text-gray-400 opacity-0 group-hover:opacity-100').addClass('text-blue-600 opacity-100');
            if (nextDirection === 'desc') $icon.addClass('rotate-180');

            // Trigger custom event so page script can fetch new data from Flask
            this.$el.trigger('ui:sort', { column: column, direction: nextDirection });
        });
    }

    updateRowStyles() {
        this.$el.find('.row-checkbox').each((idx, el) => {
            const $row = $(el).closest('tr');
            if ($(el).prop('checked')) {
                $row.addClass('bg-blue-50');
            } else {
                $row.removeClass('bg-blue-50');
            }
        });
    }

    /**
     * Utility method for API calls
     * @returns {Array} List of selected row values (e.g., IDs)
     */
    getSelectedValues() {
        return this.$el.find('.row-checkbox:checked').map(function() {
            return $(this).val();
        }).get();
    }
}

window.UI.table = Table;