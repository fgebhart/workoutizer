from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# custom error handler
handler404 = "wkz.views.custom_400_view"
handler500 = "wkz.views.custom_500_view"
handler403 = "wkz.views.custom_400_view"
handler400 = "wkz.views.custom_400_view"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("wkz.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
