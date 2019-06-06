from django.contrib import admin

from .models import Sport, Activity, Settings

admin.site.register(Sport)
admin.site.register(Activity)
admin.site.register(Settings)
