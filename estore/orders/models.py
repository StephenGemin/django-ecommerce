from PIL import Image
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    """Link between Item and Order"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
