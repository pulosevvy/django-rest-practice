from django.contrib import admin

from salon.models import Service, User, Cart, Order

admin.site.register(Service)
admin.site.register(User)
admin.site.register(Cart)
admin.site.register(Order)
