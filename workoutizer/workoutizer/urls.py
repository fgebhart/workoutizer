"""wizer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# custom error handler
handler404 = 'wizer.views.custom_404_view'
handler500 = 'wizer.views.custom_404_view'
handler403 = 'wizer.views.custom_404_view'
handler400 = 'wizer.views.custom_404_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wizer.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
