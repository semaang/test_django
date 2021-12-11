from django.contrib import admin
from primeflix_app.models import Product, StreamPlatformList, Review, Customer, Order, OrderLine, ShippingAddress

# Register your models here.

admin.site.register(Product)
admin.site.register(StreamPlatformList)
admin.site.register(Review)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(ShippingAddress)