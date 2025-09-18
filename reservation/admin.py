

# Register your models here.
# reservation/admin.py

from django.contrib import admin
from .models import Bus, Booking

# This makes the Bus and Booking models appear in the admin panel
admin.site.register(Bus)
admin.site.register(Booking)
