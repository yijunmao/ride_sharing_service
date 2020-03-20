from django.contrib import admin
from .models import Ride, Sharer, Vehicle, Driver
# Register your models here.
admin.site.register(Ride)
admin.site.register(Sharer)
admin.site.register(Vehicle)
admin.site.register(Driver)
