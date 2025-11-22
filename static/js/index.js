// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    const wishlistButtons = document.querySelectorAll('.wishlist-button');

    wishlistButtons.forEach((button) => {
        button.addEventListener('click', async function (e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent card click

            const productId = button.dataset.productId;
            const icon = button.querySelector('.wishlist-icon');
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            if (!productId) {
                console.error('Product ID not found');
                return;
            }

            try {
                const response = await fetch(`/favorites/toggle/${productId}/`, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (data.success) {
                    // Update icon based on current state
                    if (data.is_favorite) {
                        icon.src = '/static/images/redWishlist.svg';
                    } else {
                        icon.src = '/static/images/wishlist.svg';
                    }
                    const favoritesCountElement = document.getElementById('favorites-count');
                    if (favoritesCountElement && data.favorites_count !== undefined) {
                        favoritesCountElement.textContent = data.favorites_count;
                    }
                } else {
                    console.error('Error:', data.message);
                    alert('Ошибка: ' + data.message);
                }

            } catch (error) {
                console.error('Error toggling favorite:', error);
                alert('Ошибка при добавлении в избранное');
            }
        });
    });
});
