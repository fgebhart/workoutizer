from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# custom error handler
handler404 = "wizer.views.custom_404_view"
handler500 = "wizer.views.custom_404_view"
handler403 = "wizer.views.custom_404_view"
handler400 = "wizer.views.custom_404_view"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("wizer.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
