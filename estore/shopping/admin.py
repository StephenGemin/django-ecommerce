from django.contrib import admin

from . import models as m


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ordered",
        "ordered_date",
        "delivery",
        "received",
        "refund_request",
        "refund_complete",
        "billing_address",
        "payment",
        "coupon",
    )
    list_display_links = ("user", "billing_address", "payment", "coupon")
    list_filter = (
        "user",
        "ordered",
        "ordered_date",
        "delivery",
        "received",
        "refund_request",
        "refund_complete",
    )
    search_fields = ("user__username", "ref_code")


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["item", "quantity", "ordered", "user"]


class BillAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "address", "address2", "country", "postal_code"]


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "active",
        "discount_value",
        "discount_uom",
        "date_start",
        "date_end",
    ]


admin.site.register(m.Item)
admin.site.register(m.Order, OrderAdmin)
admin.site.register(m.OrderItem, OrderItemAdmin)
admin.site.register(m.BillingAddress, BillAddressAdmin)
admin.site.register(m.Payment)
admin.site.register(m.Coupon, CouponAdmin)
