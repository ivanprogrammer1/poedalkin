from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('page/registration', TemplateView.as_view(template_name="pages/registration.html")),
    path('', include('catalog.urls'), name="catalog"),
    path('', include('user.urls'), name="user"),
    path('', include('shop.urls'), name="shop"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)