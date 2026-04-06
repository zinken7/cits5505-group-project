class Carousel {
    constructor(element) {
        this.$el = $(element);
        this.$track = this.$el.find('.carousel-track');
        this.$btnNext = this.$el.find('.carousel-next');
        this.$btnPrev = this.$el.find('.carousel-prev');
        
        // Parse scroll amount from data attribute
        this.scrollAmount = parseInt(this.$el.data('scroll-amount')) || 300; 
        this.init();
    }

    init() {
        this.$btnNext.on('click', (e) => {
            e.preventDefault();
            this.scroll(this.scrollAmount, 'next');
        });

        this.$btnPrev.on('click', (e) => {
            e.preventDefault();
            this.scroll(-this.scrollAmount, 'prev');
        });
    }

    scroll(amount, direction) {
        const el = this.$track[0];
        const maxScrollLeft = el.scrollWidth - el.clientWidth;
        const currentScroll = this.$track.scrollLeft();
        
        let targetScroll = currentScroll + amount;

        // Tolerance of 5px for floating point rendering issues
        if (direction === 'next' && currentScroll >= maxScrollLeft - 5) {
            // Reached the end, rewind to start
            targetScroll = 0; 
        } else if (direction === 'prev' && currentScroll <= 5) {
            // Reached the start, fast-forward to end
            targetScroll = maxScrollLeft; 
        }

        // Animate smoothly
        this.$track.animate({
            scrollLeft: targetScroll
        }, 400);
    }
}

window.UI.carousel = Carousel;