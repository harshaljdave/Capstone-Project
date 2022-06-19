from django.contrib import admin
from .models import User, listings, bids, comments
# Register your models here.

admin.site.register(User)
admin.site.register(listings)
admin.site.register(bids)
admin.site.register(comments)
