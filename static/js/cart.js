document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".add-to-cart");
    const cartCount = document.getElementById("cart-count");

    buttons.forEach((button) => {
        button.addEventListener("click", function () {
            const productId = button.getAttribute("data-product-id");

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.cookie.match(/csrftoken=([^;]+)/)[1],
                },
            })
                .then((response) => {
                    if (response.status === 401) {
                        return;
                    }
                    return response.json();
                })
                .then(({cart_count}) => {
                    if (cart_count !== undefined) {
                        cartCount.textContent = cart_count;  // Обновляем количество в корзине
                    }
                })
                .catch(console.error);
        });
    });
});

document.getElementById('mobile-menu-button').addEventListener('click', function () {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('hidden');
});

document.on
