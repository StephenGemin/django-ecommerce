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

from . import db_util
from .forms import CheckoutForm, CouponForm
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10
    ordering = ("price",)
    context_object_name = "items_obj"


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


class CheckoutView(LoginRequiredMixin, FormView):
    form_class = CheckoutForm
    template_name = "checkout-page.html"

    def _validate_form(self, form):
        if form["billing_address"].value() == "123":
            # This particular statement was added for testing purposes,
            # but could easily be extended to verify fields
            form.add_error("billing_address", "Invalid billing address")

    def _get_billing_address_data(self, form):
        _dict = {
            "user": self.request.user,
            "address": form.cleaned_data.get("billing_address"),
            "address2": form.cleaned_data.get("billing_address2"),
            "country": form.cleaned_data.get("billing_country"),
            "postal_code": form.cleaned_data.get("billing_postal_code"),
            # TODO: add functionality for these fields
            # form.cleaned_data.get("same_shipping_address"),
            # form.cleaned_data.get("set_default_billing"),
        }
        return BillingAddress.objects.get_or_create(**_dict)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = {
            "order_obj": db_util.get_user_order(self.request),
            "coupon_form": CouponForm(),
            "DISPLAY_COUPON_FORM": True,
        }
        context.update(_dict)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        self._validate_form(form)
        if form.is_valid():
            bill_addr, created = self._get_billing_address_data(form)
            if created:
                bill_addr.save()
            order = db_util.get_user_order(self.request)
            order.billing_address = bill_addr
            order.save()

            payment_option = form.cleaned_data.get("payment_option").lower()
            self.success_url = reverse_lazy(f"shopping:payment-{payment_option}")
            return self.form_valid(form)
        else:
            messages.error(self.request, "Order UNSUCCESSFUL")
            return self.form_invalid(form)


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
