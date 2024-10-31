"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cart import views

app_name = "cart"
urlpatterns = [
    path('add_cart/<int:i>', views.add_cart, name="add_cart"),
    path('cartview', views.cart_view, name="cartview"),
    path('cartremove/<int:i>', views.cart_remove, name="cartremove"),
    path('cartdelete/<int:i>', views.cart_delete, name="cartdelete"),
    path('checkout', views.checkout, name="checkout"),
    path('status/<u>', views.payment_status, name="status"),
    path('orders', views.orders, name="orders"),
    path('add_category', views.add_category, name="add_category"),
    path('add_product', views.add_product, name="add_product"),

]
