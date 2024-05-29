from django.contrib import admin
from django.apps import apps

blog_models = apps.get_app_config('blog').get_models()

# Register your models here.
for model in blog_models:
    admin.site.register(model)