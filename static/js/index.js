document.addEventListener('DOMContentLoaded', function() {
    const wishlistButtons = document.querySelectorAll('.wishlist-button');
    const wishlistIcons = document.querySelectorAll('.wishlist-icon');

    wishlistButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const icon = wishlistIcons[index];  // Получаем соответствующую иконку для этой кнопки
            if (icon.src.includes('wishlist.svg')) {
                icon.src = '/static/images/redWishlist.svg';
            } else {
                icon.src = '/static/images/wishlist.svg';
            }
        });
    });
});
