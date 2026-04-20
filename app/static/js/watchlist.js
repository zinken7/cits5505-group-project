/**
 * Watchlist functionality for adding movies to user watchlist
 */

document.addEventListener('DOMContentLoaded', function() {
    const addToWatchlistBtns = document.querySelectorAll('.add-to-watchlist-btn');
    
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    const token = csrfToken ? csrfToken.getAttribute('content') : '';
    
    addToWatchlistBtns.forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const mediaId = this.getAttribute('data-media-id');
            const mediaType = this.getAttribute('data-media-type');
            const mediaTitle = this.getAttribute('data-media-title');
            const originalText = this.innerHTML;
            
            try {
                this.disabled = true;
                this.innerHTML = '<span class="text-lg">⏳</span> <span>Adding...</span>';
                
                const response = await fetch('/api/v1/watchlist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': token
                    },
                    body: JSON.stringify({
                        mediaId: parseInt(mediaId),
                        mediaType: mediaType,
                        status: 'planned'
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    this.innerHTML = '<span class="text-lg">✓</span> <span>Added!</span>';
                    this.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                    this.classList.add('bg-green-600', 'cursor-not-allowed');
                    this.disabled = true;
                } else {
                    const errorMsg = data.message || 'Failed to add to watchlist';
                    throw new Error(errorMsg);
                }
            } catch (error) {
                console.error('Error adding to watchlist:', error);
                const errorMessage = error.message || 'Failed';
                this.innerHTML = `<span class="text-lg">⚠</span> <span>${errorMessage}</span>`;
                this.classList.add('bg-yellow-600');
                this.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('bg-yellow-600');
                    this.classList.add('bg-blue-600', 'hover:bg-blue-700');
                    this.disabled = false;
                }, 3000);
            }
        });
    });
});


