from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, TemplateView, DetailView

from .models import Item, OrderItem, Order


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10
    context_object_name = "items_obj"


class CheckoutView(TemplateView):
    template_name = "checkout-page.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"
    context_object_name = "item_obj"


def _get_user_orders(request):
    return Order.objects.filter(user=request.user, ordered=False)


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, order_item_created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_qs = _get_user_orders(request)
    if order_qs.exists():
        order = order_qs[0]  # only one order per user at a time?
        # check if order item is in the order
        if order_item_created:
            messages.info(request, "Item added to your cart")
            order.items.add(order_item)
        else:  # add order item to order
            messages.info(request, "Item is already in the cart")
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)
    return redirect("orders:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = _get_user_orders(request)
    if order_qs.exists():
        order = order_qs[0]  # only one order per user at a time?
        # check if order item is in the order
        order_item_qs = OrderItem.objects.filter(
            item=item, user=request.user, ordered=False
        )
        if order_item_qs.exists():
            order_item_qs[0].delete()
            messages.info(request, "Item removed from your cart")
        else:
            messages.info(request, "Item is not in your cart")
            pass
    else:
        messages.info(request, "You do not have an active order")
        pass
    return redirect("orders:product", slug=slug)

# I wasn't really agreeing with the approach in the video to increase the quantity
# for 'add-to-cart" but not when removing from cart.
# Adding these copies here in case I want to revisit

# def increase_quantity(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_item, order_item_created = OrderItem.objects.get_or_create(
#         item=item, user=request.user, ordered=False
#     )
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]  # only one order per user at a time?
#         # check if order item is in the order
#         if order_item_created:
#             order.items.add(order_item)
#         else:  # add order item to order
#             # each product should have it's own unique slug right?
#             order_item.quantity += 1
#             if order_item.quantity == 1:
#                 order.items.add(order_item)
#             order_item.save()
#     else:
#         order = Order.objects.create(user=request.user, ordered_date=timezone.now())
#         order.items.add(order_item)
#     return redirect("orders:product", slug=slug)
#
# def reduce_quantity(request, slug):
# item = get_object_or_404(Item, slug=slug)
# order_item, order_item_created = OrderItem.objects.get_or_create(
#     item=item,
#     user=request.user,
#     ordered=False
# )
# order_qs = Order.objects.filter(user=request.user, ordered=False)
# if order_qs.exists():
#     order = order_qs[0]  # only one order per user at a time?
#     # check if order item is in the order
#     if order_item_created:
#         # TODO: add message saying the item is not in the order yet
#         pass
#     else:
#         # each product should have it's own unique slug right?
#         order_item.quantity -= 1
#         if order_item.quantity == 0:
#             order.items.remove(order_item)
#         if order_item.quantity < 0:
#             order_item.quantity = 0
#         order_item.save()
# else:
#     # TODO: add a message saying the user doesn't have an order
#     pass
# return redirect("orders:product", slug=slug)