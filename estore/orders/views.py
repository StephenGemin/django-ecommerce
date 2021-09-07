from django.shortcuts import render
from django.views.generic import ListView

from .models import Item


class ItemListView(ListView):
    model = Item
    template_name = "home-page.html"
    context_object_name = "items"

    def get_context_data(self):
        return {"items": ["item1", "item2"]}
