class Badge {
    constructor(element) {
        this.$el = $(element);
        this.$dismissBtn = this.$el.find('[data-dismiss="badge"]');
        this.init();
    }

    init() {
        if (this.$dismissBtn.length) {
            this.$dismissBtn.on('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.dismiss();
            });
        }
    }

    dismiss() {
        this.$el.fadeOut(200, () => {
            this.$el.remove();
        });
    }
}

window.UI.badge = Badge;