from django.contrib import admin

from .models import User, Companies

admin.site.register(User)
admin.site.register(Companies)