from django.contrib import admin

from . import models as m

admin.site.register(m.Item)
admin.site.register(m.Order)
admin.site.register(m.OrderItem)
admin.site.register(m.BillingAddress)
admin.site.register(m.Payment)
