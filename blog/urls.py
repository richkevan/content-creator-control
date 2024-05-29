from django.urls import path
from .views import Blog_Views

urlpatterns = [
    path('', Blog_Views.as_view(), name='Blogs'),
]