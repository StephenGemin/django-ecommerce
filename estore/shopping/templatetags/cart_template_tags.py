from django import template

from ..models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    # TODO: implement faster alternative.  The code below results in an extra 1+ sec
    #  for every page load/refresh.
    #  It appears the exist and count check are taking the most time ... based on
    #  profiling results from the django debug toolbar
    # if user.is_authenticated:
    #     qs = Order.objects.filter(user=user, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()
    return 1
