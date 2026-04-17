class Toggle {
    constructor(element) {
        this.$el = $(element);
        this.$input = this.$el.find('input[type="checkbox"]');
        this.init();
    }

    init() {
        this.$el.on('click', (e) => {
            if (this.$input.prop('disabled')) return;
            if (e.target !== this.$input[0]) {
                this.$input.prop('checked', !this.$input.prop('checked')).trigger('change');
            }
        });
    }
}

window.UI.toggle = Toggle;
