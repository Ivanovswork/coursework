from django.contrib import admin

from .models import (User,
                     Companies,
                     Support_Messages,
                     Books,
                     Comments,
                     Comments_Books,
                     Comments_Authors,
                     Authors,
                     Genres,
                     Groups,
                     Relations_books,
                     Purchases)

admin.site.register(User)
admin.site.register(Companies)
admin.site.register(Support_Messages)
admin.site.register(Books)
admin.site.register(Comments)
admin.site.register(Comments_Books)
admin.site.register(Comments_Authors)
admin.site.register(Authors)
admin.site.register(Genres)
admin.site.register(Groups)
admin.site.register(Relations_books)
admin.site.register(Purchases)