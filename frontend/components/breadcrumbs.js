const BREADCRUMB_SEPARATOR = `
            <svg class="h-4 w-4 shrink-0 text-muted/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
        `;

function buildBreadcrumbHtml(items) {
    let html = '<ol class="flex items-center flex-wrap gap-x-2 gap-y-1 text-sm text-muted">';

    items.forEach((item, index) => {
        const isLast = index === items.length - 1;

        html += `<li><div class="flex items-center">`;

        if (index > 0) {
            html += BREADCRUMB_SEPARATOR;
        }

        if (isLast || !item.url) {
            html += `<span class="ml-2 font-medium text-foreground">${item.label}</span>`;
        } else {
            html += `<a href="${item.url}" class="${index > 0 ? 'ml-2 ' : ''}hover:text-foreground transition-colors">${item.label}</a>`;
        }

        html += `</div></li>`;
    });

    html += '</ol>';
    return html;
}

class Breadcrumbs {
    constructor(element) {
        this.$el = $(element);
        const raw = this.$el.attr('data-items');
        if (!raw || this.$el.find('ol').length) {
            return;
        }
        try {
            const items = JSON.parse(raw);
            if (Array.isArray(items) && items.length > 0) {
                this.setItems(items);
            }
        } catch (e) {
            /* ignore invalid JSON */
        }
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

        this.$el.html(buildBreadcrumbHtml(items));
    }
}

window.UI.breadcrumbs = Breadcrumbs;
