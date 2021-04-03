from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# custom error handler
handler404 = "wkz.views.custom_404_view"
handler500 = "wkz.views.custom_404_view"
handler403 = "wkz.views.custom_404_view"
handler400 = "wkz.views.custom_404_view"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("wkz.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
