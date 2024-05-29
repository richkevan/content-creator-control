from django.contrib import admin
from django.apps import apps

gis_models = apps.get_app_config('gps_data').get_models()

# Register your models here.
for model in gis_models:
    admin.site.register(model)