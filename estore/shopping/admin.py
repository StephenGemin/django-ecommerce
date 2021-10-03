from django.contrib import admin

from . import models as m


def accept_refund(modeladmin, request, queryset):
    queryset.update(refund_request=False, refund_granted=True)


accept_refund.short_description = "Update orders to grant refund"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ordered",
        "ordered_date",
        "delivery",
        "received",
        "refund_request",
        "refund_granted",
        "billing_address",
        "shipping_address",
        "payment",
        "coupon",
    )
    list_display_links = (
        "user",
        "billing_address",
        "shipping_address",
        "payment",
        "coupon",
    )
    list_filter = (
        "user",
        "ordered",
        "ordered_date",
        "delivery",
        "received",
        "refund_request",
        "refund_granted",
    )
    search_fields = ("user__username", "ref_code")
    actions = [accept_refund]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["item", "quantity", "ordered", "user"]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "address_type",
        "address",
        "address2",
        "country",
        "postal_code",
        "default",
    ]
    list_filter = ["default", "address_type", "country"]
    search_fields = ["user", "address", "address2", "postal_code"]


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
admin.site.register(m.Address, AddressAdmin)
admin.site.register(m.Payment)
admin.site.register(m.Coupon, CouponAdmin)
admin.site.register(m.Refund)
