
from cart.models import Cart as CartModel

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get('cart', {})
        self.user = request.user

        if request.user.is_authenticated:
            self.restore_from_db(request.user)

        if not self.cart:
            self.cart = {}

        self.save()

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'price': float(product.price),
                'quantity': 0,
                'product_name': product.name,
                'image_url': product.image_url,

            }

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def get_total_count(self):
        return sum(item['quantity'] for item in self.cart.values())

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def delete(self, pr):
        product_id = str(pr)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        if self.user.is_authenticated:
            CartModel.objects.filter(user=self.user).delete()
        del self.session['cart']
        self.cart = {} # Чтобы состояние объекта совпадало с состоянием сессии
        self.save()

    def update(self, pr, quantity_change):
        product_id = str(pr)
        # Проверяем, что продукт существует в корзине
        if product_id in self.cart:
            current_quantity = self.cart[product_id]['quantity']

            new_quantity = int(current_quantity) + int(quantity_change)

            if new_quantity <= 0:
                # Удаляем продукт, если количество <= 0
                del self.cart[product_id]
                CartModel.objects.filter(user=self.user, product_id=product_id).delete()
            else:
                # Обновляем количество товара
                self.cart[product_id]['quantity'] = new_quantity
                CartModel.objects.filter(user=self.user, product_id=product_id).update(quantity=new_quantity)
            # Сохраняем изменения в сессии
            self.save()
        else:
            # Если продукта нет в корзине, генерируем ошибку
            raise ValueError(f"Product ID {product_id} not found in cart.")

    def get_total_price(self):
        return sum(float(item['price']) * float(item['quantity']) for item in self.cart.values())

    def get_cart_count(self):
        return sum(item['quantity'] for item in self.cart.values())

    def restore_from_db(self, user):
        cart_items = CartModel.objects.filter(user=user)
        for cart_item in cart_items:
            product_id = str(cart_item.product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {
                    'price': str(cart_item.product.price),
                    'quantity': cart_item.quantity,
                    'product_name': cart_item.product.name
                }
        self.save()