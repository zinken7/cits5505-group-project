class ToastManager {
    constructor() {
        this.containerId = 'ui-toast-container';
        this.initContainer();
    }

    initContainer() {
        if ($(`#${this.containerId}`).length === 0) {
            $('body').append(`
                <div id="${this.containerId}" aria-live="assertive" class="pointer-events-none fixed inset-0 flex items-end px-4 py-6 sm:items-start sm:p-6 z-[100]">
                    <div class="flex w-full flex-col items-center space-y-4 sm:items-end"></div>
                </div>
            `);
        }
        this.$container = $(`#${this.containerId} > div`);
    }

    /**
     * Show a notification toast
     * @param {string} title - Main message
     * @param {string} description - Subtext (optional)
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Time in ms before auto-close
     */
    show(title, description = '', type = 'success', duration = 3000) {
        // Define icons and colors based on type
        const styles = {
            success: { icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />', color: 'text-green-400' },
            error: { icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />', color: 'text-red-400' },
            info: { icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />', color: 'text-blue-400' }
        };

        const currentStyle = styles[type] || styles.info;
        const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);

        const html = `
            <div id="${toastId}" class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 transition transform translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2">
                <div class="p-4">
                    <div class="flex items-start">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 ${currentStyle.color}" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                ${currentStyle.icon}
                            </svg>
                        </div>
                        <div class="ml-3 w-0 flex-1 pt-0.5">
                            <p class="text-sm font-medium text-gray-900">${title}</p>
                            ${description ? `<p class="mt-1 text-sm text-gray-500">${description}</p>` : ''}
                        </div>
                        <div class="ml-4 flex flex-shrink-0">
                            <button type="button" class="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none" onclick="$('#${toastId}').fadeOut(300, function(){ $(this).remove(); })">
                                <span class="sr-only">Close</span>
                                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const $toast = $(html);
        this.$container.append($toast);

        // Animate in (Slide from right/bottom)
        setTimeout(() => {
            $toast.removeClass('translate-y-2 opacity-0 sm:translate-x-2').addClass('translate-y-0 opacity-100 sm:translate-x-0');
        }, 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                $toast.fadeOut(300, function() { $(this).remove(); });
            }, duration);
        }
    }
}

// Khởi tạo một instance duy nhất (Singleton) có thể gọi ở bất cứ đâu
window.UI.toast = new ToastManager();