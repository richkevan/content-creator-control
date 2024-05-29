from django.views import View
from django.shortcuts import render
from .models import Blog, Blog_Post, Blog_Category, Blog_Tag, Comment

# Create your views here.
class Blog_Views(View):
  def get(self, request):
    blogs = Blog.objects.all()
    return render(request, 'blog.html', {'managed_blogs': blogs})