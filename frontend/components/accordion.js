class Accordion {
    constructor(element) {
        this.$el = $(element);
        const dm = this.$el.attr("data-multiple");
        this.allowMultiple =
            this.$el.data("multiple") === true ||
            String(dm || "").toLowerCase() === "true";
        this.init();
    }

    init() {
        this.$el.on("click", ".accordion-header", (e) => {
            const $header = $(e.currentTarget);
            const $item = $header.closest(".accordion-item");
            const $content = $item.find(".accordion-content");
            const $icon = $header.find(".accordion-icon");
            const isOpen = $item.hasClass("is-open");

            if (!this.allowMultiple && !isOpen) {
                const $others = this.$el.find(".accordion-item.is-open").not($item);
                $others.each((_, el) => {
                    const $oi = $(el);
                    $oi.find(".accordion-content").slideUp(200, () => {
                        $oi.removeClass("is-open");
                    });
                });
            }

            if (isOpen) {
                $content.slideUp(200, () => {
                    $item.removeClass("is-open");
                });
            } else {
                $icon.addClass("rotate-180");
                $content.slideDown(200, () => {
                    $item.addClass("is-open");
                    $icon.removeClass("rotate-180");
                });
            }
        });
    }
}

window.UI.accordion = Accordion;
