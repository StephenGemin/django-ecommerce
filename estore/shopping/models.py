from django.conf import settings
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField

from . import constants


class Item(models.Model):
    """Individual item from store"""
    category = models.CharField(choices=constants.CATEGORY_CHOICES, max_length=30)
    description = models.TextField()
    image = models.ImageField(default="image_missing.jpg", upload_to="inventory_pics")
    label = models.CharField(choices=constants.LABEL_CHOICES, max_length=1)
    price = models.FloatField()
    price_discount = models.FloatField(blank=True, null=True)
    slug = models.SlugField()
    title = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse("shopping:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("shopping:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("shopping:remove-from-cart", kwargs={"slug": self.slug})

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
        return reverse("shopping:incre-item-quantity", kwargs={"slug": self.item.slug})

    def get_decrease_order_item_quantity_url(self):
        return reverse("shopping:decre-item-quantity", kwargs={"slug": self.item.slug})

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=30)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name="billing_address", on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    delivery = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_request = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            # percent
            if self.coupon.discount_uom == constants.COUPON_DISCOUNT_UOM[0][0]:
                total /= 1 + (self.coupon.discount_value / 100)
            else:  # absolute
                total -= self.coupon.discount_value
            if total < 0:
                total = 0
        return total

    def __str__(self):
        return f"{self.user.username} {self.ref_code}"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    active = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    discount_value = models.FloatField()
    discount_uom = models.CharField(choices=constants.COUPON_DISCOUNT_UOM, max_length=20)

    # TODO: validation to make sure date_end > date_start
    # TODO: validation to make sure if % then value <= 100
    # TODO: map coupon or coupons to specific users, by region, birthday, etc??

    def pretty_print_coupon(self) -> str:
        if self.discount_uom == constants.COUPON_DISCOUNT_UOM[0][0]:  # percent
            return f"{int(self.discount_value)}{self.get_discount_uom_display()}"
        else:  # absolute
            return f"{self.get_discount_uom_display()}{self.discount_value:.02f}"

    def __str__(self):
        return self.code


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=1, choices=constants.ADDRESS_CHOICES)
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    country = CountryField(multiple=False)
    postal_code = models.CharField(max_length=6, unique=False)  # TODO: make unique
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Addresses"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    payment_type = models.CharField(choices=constants.PAYMENT_CHOICES, max_length=50)
    payment_obj = models.TextField()
    payment_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return str(self.order)
