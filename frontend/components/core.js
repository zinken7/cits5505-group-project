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

$(document).ready(() => {
    window.UI.init();
});