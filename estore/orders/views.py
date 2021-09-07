from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView

from .models import Item


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
