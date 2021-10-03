from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from ..models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        try:
            order = Order.objects.get(user=user, ordered=False)
            return order.items.count()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return 0

    # NOTE:
    # The following code was very slow.  It was causing an extra 1-2+ sec for
    # every page load/refresh. From django debug-toolbar, the exist and count checks
    # were taking the most time.  Especially the count.
    # Adding these here as a note to future self, as this took a while to figure out.
    # The code below was from the YouTube tutorial.

    # CODE BLOCK
    # if user.is_authenticated:
    #     qs = Order.objects.filter(user=user, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()
