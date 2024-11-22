from django.contrib import admin
from .models import User, SessionOAuth
from django.contrib.auth.admin import UserAdmin

#admin.site.unregister(User)
#admin.site.register(User)

admin.site.register(SessionOAuth)