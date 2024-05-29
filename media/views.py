from django.views import View
from django.shortcuts import render
from .models import Photo, Video, Album, Media_Tag, Media_Category, Social_Tag
from itertools import chain


root = "Media"

# Create your views here.
class GalleryView(View):
    def get(self, request):
        title = "Gallery"
        media_models = list(chain(Photo.objects.all(), Video.objects.all()))
        albums = Album.objects.all()
        media_tags = Media_Tag.objects.all()
        media_categories = Media_Category.objects.all()
        return render(request, 'gallery.html', {
            'breadcrumb':[root, title], 
            'media_list': media_models,
            'albums': albums,
            'media_tags': media_tags,
            'media_categories': media_categories
            })