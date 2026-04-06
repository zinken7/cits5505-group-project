class Tabs {
    constructor(element) {
        this.$el = $(element);
        this.$buttons = this.$el.find('[data-tab-target]');
        this.init();
    }

    init() {
        this.$buttons.on('click', (e) => {
            e.preventDefault();
            const $clickedTab = $(e.currentTarget);
            const targetId = $clickedTab.data('tab-target');
            
            this.activate(targetId, $clickedTab);
        });
    }

    /**
     * Activate a specific tab and its panel
     * @param {string} targetId - ID of the panel to show
     * @param {jQuery} $tabBtn - The jQuery object of the clicked tab
     */
    activate(targetId, $tabBtn) {
        // 1. Update Tab Buttons UI
        this.$buttons.removeClass('border-blue-500 text-blue-600')
                     .addClass('border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300');
        
        $tabBtn.removeClass('border-transparent text-gray-500')
               .addClass('border-blue-500 text-blue-600');

        // 2. Update Panels
        const $targetPanel = $(targetId);
        if ($targetPanel.length) {
            // Hide all sibling panels
            $targetPanel.parent().children().addClass('hidden');
            // Show target panel
            $targetPanel.removeClass('hidden');
        }
    }
}

window.UI.tabs = Tabs;