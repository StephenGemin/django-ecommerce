from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home-page"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout-page"),
    path('product/<slug>/', views.ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"),
    path('order-summary/incre/<slug>/', views.increase_order_item_quantity, name="incre-item-quantity"),
    path('order-summary/decre/<slug>/', views.decrease_order_item_quantity, name="decre-item-quantity"),
]
