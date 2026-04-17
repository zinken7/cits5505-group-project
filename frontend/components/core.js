window.UI = window.UI || {};

window.UI.init = function(context = document) {
    $(context).find('[data-ui]').each(function() {
        const $el = $(this);
        const componentName = $el.data('ui');
        
        if (window.UI[componentName] && !$el.data('nuxt-ui-instance')) {
            const instance = new window.UI[componentName](this);
            $el.data('nuxt-ui-instance', instance);
        }
    });
};

// Init is driven from frontend/src/main.js after import "./style.css" so layout does not shift
// when components (accordion, etc.) run before Tailwind is applied.