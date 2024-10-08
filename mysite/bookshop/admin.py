from django.contrib import admin

from .models import User, Companies, Support_Messages, Books

admin.site.register(User)
admin.site.register(Companies)
admin.site.register(Support_Messages)
admin.site.register(Books)