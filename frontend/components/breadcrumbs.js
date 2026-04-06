class Breadcrumbs {
    constructor(element) {
        this.$el = $(element);
    }

    /**
     * Re-renders the breadcrumb trail
     * @param {Array} items - Array of objects: [{ label: 'Home', url: '/' }, { label: 'Settings' }]
     */
    setItems(items) {
        if (!Array.isArray(items) || items.length === 0) {
            this.$el.empty();
            return;
        }

        let html = '<ol class="flex items-center space-x-2 text-sm text-gray-500">';
        
        const separator = `
            <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
        `;

        items.forEach((item, index) => {
            const isLast = index === items.length - 1;
            
            html += `<li><div class="flex items-center">`;
            
            if (index > 0) {
                html += separator;
            }

            if (isLast || !item.url) {
                // Active/Last item (No link)
                html += `<span class="ml-2 font-medium text-gray-900">${item.label}</span>`;
            } else {
                // Clickable link
                html += `<a href="${item.url}" class="${index > 0 ? 'ml-2 ' : ''}hover:text-gray-900 transition-colors">${item.label}</a>`;
            }
            
            html += `</div></li>`;
        });

        html += '</ol>';
        this.$el.html(html);
    }
}

window.UI.breadcrumbs = Breadcrumbs;