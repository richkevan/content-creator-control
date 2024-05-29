from django.contrib import admin
from django.apps import apps

media_models = apps.get_app_config('media').get_models()

# Register your models here.
for model in media_models:
    admin.site.register(model)