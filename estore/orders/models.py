from django.conf import settings
from django.db import models


class Item(models.Model):
    """Individual item from store"""
    title = models.CharField(max_length=200)
    price = models.FloatField()

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
