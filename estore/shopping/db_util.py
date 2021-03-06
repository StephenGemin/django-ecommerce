import uuid

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Order, Coupon


def get_user_order(request):
    try:
        return Order.objects.get(user=request.user, ordered=False)
    except ObjectDoesNotExist:
        messages.error(request, "You do not have an active order")
        return None


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
    except ObjectDoesNotExist:
        messages.error(request, f"Coupon '{code}' does not exist")
        return None

    now = timezone.now()
    if not coupon.active:
        messages.error(request, f"Coupon '{code}' is no longer valid or active")
        return None
    elif now > coupon.date_end:
        messages.error(request, f"Coupon '{code}' has expired.")
        return None
    return coupon


def filter_user_orders(request):
    return Order.objects.filter(user=request.user, ordered=False)


def update_order_after_payment(order, payment):
    order.ordered = True
    order.payment = payment
    order.ref_code = generate_ref_code()
    order.save()


def update_order_items_after_payment(order):
    order_items = order.items.all()
    order_items.update(ordered=True)
    for o_item in order_items:
        o_item.save()


def update_coupon_after_payment(order):
    coupon = order.coupon
    if not coupon:
        return
    coupon.active = False
    coupon.save()


def generate_ref_code():
    return uuid.uuid4()
