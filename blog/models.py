from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Blog_Category(models.Model):
    category = models.SlugField(max_length=255)
    
    def __str__(self):
        return self.category
      
class Blog_Tag(models.Model):
    tag = models.SlugField(max_length=255)
    
    def __str__(self):
        return self.tag

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return f"/blog/{self.id}"
    def get_edit_url(self):
        return f"/blog/{self.id}/edit"
    def get_delete_url(self):
        return f"/blog/{self.id}/delete"
      
class Blog_Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    schedule = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Blog_Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Blog_Tag)
    
    def __str__(self):
        return self.title
    
      
class Comment(models.Model):
    post = models.ForeignKey(Blog_Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name