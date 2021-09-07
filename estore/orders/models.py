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
    title = models.CharField(max_length=200)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    price_discount = models.FloatField(
        blank=True, null=True, validators=[MaxValueValidator(price)]
    )
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()

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
