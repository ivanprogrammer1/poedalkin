from django.urls import path
from .views import *

urlpatterns = [
    path("user/login", LoginView.as_view(), name="login"),
    path("user/app/code", AuthCodeView.as_view(), name="app_code"),
    path("user/app/token", AccessCodeView.as_view(), name="app_token"),
    path("user/app/refresh", RefreshCodeView.as_view(), name="app_refresh"),
    path("user/app/active", checkActiveToken, name="app_check"),
    
    path("api/user.get", UserView.as_view(), name="user.get"),
    path("api/user.update", UserUpdateView.as_view(), name="user.update")
]
