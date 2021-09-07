from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home-page"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout-page"),
    path('products/', views.ProductPageView.as_view(), name="product-page"),
]
