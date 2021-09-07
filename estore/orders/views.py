from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from .models import Item


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10
    context_object_name = "items"


class CheckoutView(TemplateView):
    template_name = "checkout-page.html"


class ProductPageView(TemplateView):
    template_name = "product-page.html"
