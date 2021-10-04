from contextlib import suppress
from typing import Tuple, List

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView,
    TemplateView,
    DetailView,
    FormView,
)

import stripe
from stripe import error as stripe_error

from . import db_util, constants
from .forms import CheckoutForm, CouponForm, RefundForm
from .models import Item, OrderItem, Order, Address, Payment, Refund


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10
    ordering = ("price",)
    context_object_name = "items_obj"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = {
            "categories": constants.CATEGORY_CHOICES
        }
        context.update(_dict)
        return context


class HomeViewByCategory(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10
    ordering = ("price",)
    context_object_name = "items_obj"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = {
            "categories": constants.CATEGORY_CHOICES,
            "active_category": self.kwargs.get("category")
        }
        context.update(_dict)
        # breakpoint()
        return context

    def get_queryset(self):
        category = self.kwargs.get("category")
        return self.model.objects.filter(category=category).order_by("price")


class OrderSummaryView(LoginRequiredMixin, TemplateView):
    model = Order
    template_name = "order_summary.html"
    context_object_name = "order_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            query_result = db_util.get_user_order(self.request)
            context[self.context_object_name] = query_result
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            context[self.context_object_name] = None
        return context


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, FormView):
    form_class = CheckoutForm
    template_name = "checkout-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = {
            "order_obj": db_util.get_user_order(self.request),
            "coupon_form": CouponForm(),
            "DISPLAY_COUPON_FORM": True,
        }
        context.update(_dict)

        shipping_address_qs = Address.objects.filter(
            user=self.request.user, address_type="S", default=True
        )
        if shipping_address_qs.exists():
            context.update({"default_shipping_address": shipping_address_qs[0]})

        billing_address_qs = Address.objects.filter(
            user=self.request.user, address_type="B", default=True
        )
        if billing_address_qs.exists():
            context.update({"default_billing_address": billing_address_qs[0]})
        return context

    def _validate_address(self, form, address: Address, address_type: str):
        fields = ["address", "country", "postal_code"]
        for f in fields:
            field_value = getattr(address, f)
            if field_value == "" or field_value is None:
                form.add_error(f"{address_type}_{f}", "Field must have a value")

        if address.address == "000":
            # This particular statement was added for testing purposes,
            # but could easily be extended to verify fields
            form.add_error(f"{address_type}_address", "Invalid address value")

    def _get_address_data(self, form, address_type: str) -> dict:
        if address_type == "B":
            addr = "billing"
        elif address_type == "S":
            addr = "shipping"
        else:
            raise ValueError(
                f"invalid address type passed: {address_type}. "
                f"Expected values ('B', 'S')"
            )
        return {
            "user": self.request.user,
            "address": form.cleaned_data.get(f"{addr}_address"),
            "address2": form.cleaned_data.get(f"{addr}_address2"),
            "country": form.cleaned_data.get(f"{addr}_country"),
            "postal_code": form.cleaned_data.get(f"{addr}_postal_code"),
            "address_type": address_type,
        }

    def _process_form_address(
        self, form, address_type: Tuple[str, str], use_default: bool, set_default: bool
    ) -> Address:
        addr_key, addr_value = address_type
        if use_default:
            try:
                addr = Address.objects.get(
                    user=self.request.user, default=True, address_type=addr_key
                )
            except ObjectDoesNotExist:
                messages.error(
                    self.request, f"No default {addr_value} address available"
                )
                return redirect("shopping:checkout-page")
        else:
            addr_data = self._get_address_data(form, addr_key)
            try:
                addr = Address.objects.get(**addr_data)
            except ObjectDoesNotExist:
                addr = Address(**addr_data)

            self._validate_address(form, addr, addr_value)
            if not form.is_valid():
                messages.error(self.request, f"Invalid {addr_value} address fields")
                return self.form_invalid(form)

        if set_default and addr.default is False:
            with suppress(ObjectDoesNotExist):
                current_default = Address.objects.get(
                    user=self.request.user, default=True, address_type=addr_key
                )
                current_default.default = False
                current_default.save()
                addr.default = True
        addr.save()
        return addr

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if not form.is_valid():
            messages.error(self.request, "Error processing form")
            return self.form_invalid(form)
        use_default_shipping = form.cleaned_data.get("use_default_shipping")
        set_default_shipping = form.cleaned_data.get("set_default_shipping")
        use_default_billing = form.cleaned_data.get("use_default_billing")
        set_default_billing = form.cleaned_data.get("set_default_billing")

        ship_addr = self._process_form_address(
            form,
            constants.ADDRESS_CHOICES[1],
            use_default_shipping,
            set_default_shipping,
        )
        bill_addr = self._process_form_address(
            form, constants.ADDRESS_CHOICES[0], use_default_billing, set_default_billing
        )

        order = db_util.get_user_order(self.request)
        order.billing_address = bill_addr
        order.shipping_address = ship_addr
        order.save()

        payment_option = form.cleaned_data.get("payment_option").lower()
        self.success_url = reverse_lazy(f"shopping:payment-{payment_option}")
        return self.form_valid(form)


class StripePaymentView(LoginRequiredMixin, TemplateView):
    template_name = "payment_stripe_form.html"
    # Public key passed into context is ESSENTIAL.  Failure to do this will result
    # in a CardError when processing payment
    # this stupid step took a couple of hours to figure out
    # Invalid request: Request req_6tE0kAQlyod8wY: Must provide source or customer.
    extra_context = {"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = {
            "order_obj": db_util.get_user_order(self.request),
            "coupon_form": CouponForm(),
            "DISPLAY_COUPON_FORM": False,
        }
        context.update(_dict)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context["order_obj"].billing_address:
            return self.render_to_response(context)
        else:
            messages.error(request, "You must add a billing address")
            return redirect("shopping:checkout-page")

    def post(self, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        order = db_util.get_user_order(self.request)
        if order is None:
            return redirect("shopping:home-page")
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token  # noqa: E501
        token = self.request.POST.get("stripeToken")
        amount = order.get_total()

        try:
            # Stripe testing reference:  https://stripe.com/docs/testing
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                # stripe requires integer in cents for decimal currencies
                amount=int(amount * 100),
                currency="usd",
                source=token,
                description="My First Test Charge (created for API docs)",
            )
        except stripe_error.CardError as e:
            # Since it's a decline, stripe_error.CardError will be caught
            messages.error(self.request, e)
            return redirect("shopping:payment-stripe")
        except stripe_error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"{e.__class__.__name__}: {e}")
            return redirect("/")
        except stripe_error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, f"Invalid request: {e}")
            print(e.json_body)
            print(e.http_body)
            return redirect("/")
        except stripe_error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, f"{e.__class__.__name__}: {e}")
            return redirect("/")
        except stripe_error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, f"{e.__class__.__name__}: {e}")
            return redirect("/")
        except stripe_error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, f"{e.__class__.__name__}: {e}")
            return redirect("/")
        except Exception as e:
            # TODO: Send email to yourself
            messages.error(self.request, "Very serious error occurred ... TBD")
            return redirect("/")

        payment = Payment(
            user=self.request.user,
            payment_type="Stripe",
            payment_obj=charge,
            payment_id=charge.get("id"),
            amount=amount,
        )
        payment.save()

        db_util.update_order_after_payment(order, payment)
        db_util.update_order_items_after_payment(order)
        db_util.update_coupon_after_payment(order)
        messages.success(
            self.request, "Your payment was successful and your order is on the way!"
        )
        return redirect("/")  # TODO: redirect to payment success page


class PayPalPaymentView(LoginRequiredMixin, TemplateView):
    template_name = "payment_paypal_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_obj"] = db_util.get_user_order(self.request)
        return context


class BitCoinPaymentView(LoginRequiredMixin, TemplateView):
    template_name = "payment_bitcoin_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_obj"] = db_util.get_user_order(self.request)
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"
    context_object_name = "item_obj"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, order_item_created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_qs = db_util.filter_user_orders(request)
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
    return redirect("shopping:product", slug=slug)


def _increment_order_item_quantity(request, slug, value: int):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[
        0
    ]
    order_item.quantity += value
    if order_item.quantity < 0:
        order_item.quantity = 0
    return order_item


@login_required
def remove_from_cart(request, slug):
    order_item = _increment_order_item_quantity(request, slug, 0)
    order_item.delete()
    msg = f"{order_item.item.title} was removed from your cart"
    messages.info(request, msg)
    return redirect("shopping:order-summary")


@login_required
def increase_order_item_quantity(request, slug):
    order_item = _increment_order_item_quantity(request, slug, 1)
    order_item.save()
    return redirect("shopping:order-summary")


@login_required
def decrease_order_item_quantity(request, slug):
    order_item = _increment_order_item_quantity(request, slug, -1)
    if order_item.quantity == 0:
        order_item.delete()
    else:
        order_item.save()
    return redirect("shopping:order-summary")


class AddCouponView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        order = db_util.get_user_order(self.request)
        if order is None:
            return redirect("shopping:checkout-page")

        form = CouponForm(self.request.POST or None)
        if not form.is_valid():
            return redirect("shopping:checkout-page")

        code = form.cleaned_data.get("code")
        coupon = db_util.get_coupon(self.request, code)
        if coupon is not None:
            order.coupon = coupon
            order.save()
            messages.success(self.request, "Your coupon was successfully processed")
        return redirect("shopping:checkout-page")


class RequestRefundView(LoginRequiredMixin, FormView):
    form_class = RefundForm
    template_name = "request_refund.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            messages.error(self.request, "Invalid form entries, please try again")
            return redirect("shopping-request-refund")

        f_data = form.cleaned_data
        ref_code = f_data.get("ref_code")
        reason = f_data.get("reason")
        email = f_data.get("email")
        try:
            order = Order.objects.get(ref_code=ref_code)
        except ObjectDoesNotExist:
            messages.error(self.request, "Invalid reference code")
            return redirect("shopping:request-refund")

        order.refund_request = True
        order.save()

        with suppress(ObjectDoesNotExist):
            refund = Refund.objects.get(order=order)
            messages.info(
                self.request, "Refund already request for given order reference code"
            )
            return redirect("shopping:home-page")

        refund = Refund()
        refund.order = order
        refund.reason = reason
        refund.email = email
        refund.save()

        messages.info(self.request, "Your request was received")
        return redirect("shopping:home-page")
