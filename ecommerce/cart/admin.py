from django.contrib import admin
from cart.models import Cart,Order_details,Payment
from django.http import HttpResponse
# Register your models here.
admin.site.register(Cart)
admin.site.register(Order_details)
admin.site.register(Payment)