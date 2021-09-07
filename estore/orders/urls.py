from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.ItemListView.as_view(), name="item-list"),
]
