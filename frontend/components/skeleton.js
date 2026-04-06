class Skeleton {
    constructor(element) {
        this.$el = $(element);
        this.$content = this.$el.find('.skeleton-content');
        this.$placeholders = this.$el.find('.skeleton-placeholder');
    }

    /**
     * Toggle loading state
     * @param {boolean} isLoading 
     */
    setLoading(isLoading) {
        if (isLoading) {
            this.$content.addClass('hidden');
            this.$placeholders.removeClass('hidden');
        } else {
            this.$placeholders.addClass('hidden');
            this.$content.removeClass('hidden');
        }
    }
}

window.UI.skeleton = Skeleton;