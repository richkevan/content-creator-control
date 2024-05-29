from django.db import models
from gps_data.models import Latitude, Longitude, Coordinate, Route
from PIL import Image, ExifTags
from hurry.filesize import size, alternative
import os
import datetime
import boto3

# Create your models here.
class Album(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.title = self.title.replace(' ', '_')
        super().save(*args, **kwargs)
    
class Media_Tag(models.Model):
    tag = models.SlugField(max_length=255)
    
    def __str__(self):
        return self.tag
    
class Social_Tag(models.Model):
    tag = models.SlugField(max_length=255)
    
    def __str__(self):
        return self.tag
    def save(self, *args, **kwargs):
        self.tag = '#' + self.tag.replace(' ', '')
        super().save(*args, **kwargs)

class Media_Category(models.Model):
    category = models.SlugField(max_length=255, null=False, blank=True)
    
    def __str__(self):
        return self.category
    
class Media(models.Model):
    def __str__(self):
        return f"{self.album}/{self.title}"
    
    def get_absolute_url(self):
        return f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/{self.album.title}/{self.title}"
    
    def upload_album(self):
        return f'{self.album.title}'
    
    def file_type(self):
        if self.imageFile:
            return self.imageFile.name.split('/')[-1].replace(' ', '_')
        elif self.videoFile:
            return self.videoFile.name.split('/')[-1].replace(' ', '_')
        
    def file_size(self):
        if self.imageFile:
            return size(self.imageFile.size, system=alternative)
        elif self.videoFile:
            return size(self.videoFile.size, system=alternative)
        
    def get_location(self):
        if self.imageFile:
            gps_data = {}
            image_open = Image.open(self.imageFile)
            image_exif = image_open._getexif()
            if image_exif:
                for tag, value in image_exif.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    print(decoded)
                    if decoded == 'DateTimeOriginal':
                        print("TIMESTAMP: ",value)
                        gps_data[decoded] = datetime.datetime.fromisoformat(value.replace(':','-',2))
                    elif decoded == 'GPSInfo':
                        print("GPSINFO: ",value)
                        if value is not None:
                            for gps_tag in value:
                                sub_decoded = ExifTags.GPSTAGS.get(gps_tag, gps_tag)
                                print("GPS TAGS", sub_decoded, value[gps_tag])
                                gps_data[sub_decoded] = value[gps_tag]                
            print("GPS_DATA: ",gps_data)
            if 'GPSLatitudeRef' in gps_data and 'GPSLongitudeRef' in gps_data:
                Latitude.objects.create(
                    label = 'Latitude',
                    ref = gps_data['GPSLatitudeRef'],
                    deg = gps_data['GPSLatitude'][0],
                    min = gps_data['GPSLatitude'][1],
                    sec = gps_data['GPSLatitude'][2]
                    )
                Longitude.objects.create(
                    label = 'Longitude',
                    ref = gps_data['GPSLongitudeRef'],
                    deg = gps_data['GPSLongitude'][0],
                    min = gps_data['GPSLongitude'][1],
                    sec = gps_data['GPSLongitude'][2]
                    )
            if Latitude.objects.last() and Longitude.objects.last():
                coorddinate = Coordinate.objects.create(
                    latitude = Latitude.objects.last(),
                    longitude = Longitude.objects.last(),
                    altitude = gps_data['GPSAltitude'] if 'GPSAltitude' in gps_data else 0.0,
                    timestamp = gps_data['DateTimeOriginal']
                    )
            return coorddinate
    
    def save(self, *args, **kwargs):
        self.album = self.album
        self.title = self.file_type()
        self.public_url = self.get_absolute_url()
        self.size = self.file_size()
        self.gps_data = self.get_location()
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        if self.imageFile:
            s3 = boto3.client('s3')
            print(s3)
            s3.delete_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key=f'{self.album.title}/{self.title}')
        elif self.videoFile:
            self.videoFile.delete()
        super().delete(*args, **kwargs)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, null=False, blank=False, default='FILENAME')
    description = models.TextField(blank=True)
    category = models.ForeignKey(Media_Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Media_Tag, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    public_url = models.URLField(default='https://nomadair-media.s3.amazonaws.com/')
    size = models.CharField(max_length=255, null=False, blank=False, default='0 mb')
    exif_data = models.TextField(blank=True)
 
    class Meta:
        abstract = True
           
class Photo(Media):
    def upload_path(instance, filename):
        instance.title = filename
        instance.public_url = instance.get_absolute_url()
        return "{0}/{1}".format(instance.album.title, filename)

    imageFile = models.ImageField(upload_to=upload_path, null=False, blank=False)
    gps_data = models.ForeignKey(Coordinate, on_delete=models.DO_NOTHING, null=True, blank=True)

class Video(Media):
    def upload_path(instance, filename):
        instance.title = filename
        instance.public_url = instance.get_absolute_url()
        return "{0}/{1}".format(instance.album.title, filename)
    
    videoFile = models.FileField(upload_to=upload_path, null=False, blank=False)
    gps_data = models.ForeignKey(Route, on_delete=models.DO_NOTHING, null=True, blank=True)

    

    
    