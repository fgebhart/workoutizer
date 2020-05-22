from django.contrib import admin

from .models import Sport, Activity, Settings, Traces, Lap

admin.site.register(Sport)
admin.site.register(Activity)
admin.site.register(Settings)
admin.site.register(Traces)
admin.site.register(Lap)
