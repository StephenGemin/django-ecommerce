from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q
from django.urls import reverse

CATEGORY_CHOICES = (
    ('All', 'All'),
    ('Outerwear', 'Outerwear'),
    ('Shirt', 'Shirt'),
    ('Sport', 'Sport'),
    ('Sportwear', 'Sport wear'),
)

LABEL_CHOICES = (
    ('D', 'danger'),
    ('P', 'primary'),
    ('S', 'secondary'),
)


class Item(models.Model):
    """Individual item from store"""
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    description = models.TextField()
    image = models.ImageField(default="image_missing.jpg", upload_to="inventory_pics")
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    price = models.FloatField()
    price_discount = models.FloatField(blank=True, null=True)
    slug = models.SlugField()
    title = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse("orders:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("orders:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("orders:remove-from-cart", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    """Link between Item and Order"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def _is_discounted(self):
        if self.item.price_discount is not None:
            return True
        return False

    def get_item_price(self):
        if self._is_discounted():
            return self.item.price_discount
        return self.item.price

    def _get_total_item_price(self):
        return self.quantity * self.item.price

    def _get_total_discount_item_price(self):
        if self._is_discounted():
            return self.quantity * self.item.price_discount

    def get_amount_saved(self):
        if self._is_discounted():
            return self._get_total_item_price() - self._get_total_discount_item_price()

    def get_final_price(self):
        if self._is_discounted():
            return self._get_total_discount_item_price()
        return self._get_total_item_price()

    def get_increase_order_item_quantity_url(self):
        return reverse("orders:incre-item-quantity", kwargs={"slug": self.item.slug})

    def get_decrease_order_item_quantity_url(self):
        return reverse("orders:decre-item-quantity", kwargs={"slug": self.item.slug})

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def __str__(self):
        return f"{self.user.username} ordered={self.ordered}"
