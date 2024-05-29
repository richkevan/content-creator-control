from typing import Iterable
from django.db import models
import requests
import os

MAP_BOX_API_KEY = os.getenv("MAPBOX_ACCESS_TOKEN")

# Create your models here.
class Geo_Info(models.Model):
        
    ref = models.CharField(max_length=1)
    deg = models.FloatField()
    min = models.FloatField()
    sec = models.FloatField()
    
    class Meta:
        abstract = True

class Latitude(Geo_Info):
    label = models.CharField(max_length=255,default='Latitude')
    
    def __str__(self):
        direction = "-" if self.ref == 'S' else ""
        return f'{direction}{self.deg + self.min/60 + self.sec/3600}'
  
class Longitude(Geo_Info):
    label = models.CharField(max_length=255,default='Longitude')
  
    def __str__(self):
        direction = "-" if self.ref == 'W' else ""
        return f'{direction}{self.deg + self.min/60 + self.sec/3600}'
    
class Coordinate(models.Model):
    latitude = models.ForeignKey(Latitude, on_delete=models.DO_NOTHING)
    longitude = models.ForeignKey(Longitude, on_delete=models.DO_NOTHING)
    altitude = models.FloatField()
    timestamp = models.DateTimeField()
    common_name = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f'{self.latitude}, {self.longitude}, {self.altitude}, {self.timestamp}'
    
    def get_absolute_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
    
    def get_location(self):
        return f"{self.latitude}, {self.longitude}"
    
    def get_altitude(self):
        return f"{self.altitude}"
    
    def get_timestamp(self):
        return f"{self.timestamp}"
    
    def save(self, *args, **kwargs):
        print(f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={self.longitude}&latitude={self.latitude}&access_token={MAP_BOX_API_KEY}")
        response = requests.get(f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={self.longitude}&latitude={self.latitude}&access_token={MAP_BOX_API_KEY}")
        data = response.json()
        base = data['features'][0]['properties']['context']
        common_name = f'{base['place']['name']}, {base['district']['name']}, {base['region']['name']}, {base['country']['name']}'
        print("REVERSE GEOCODE: ",common_name)
        self.common_name = common_name
        super().save()
    
    class Meta:
        ordering = ['-timestamp']
  
class Route(models.Model):
    start = models.ForeignKey(Coordinate, on_delete=models.DO_NOTHING, related_name='start')
    end = models.ForeignKey(Coordinate, on_delete=models.DO_NOTHING, related_name='end')
    route = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points = models.ManyToManyField(Coordinate)
    
    def __str__(self):
        return self.route
    
    def get_absolute_url(self):
        return f"https://www.google.com/maps/dir/?api=1&origin={self.points.first().latitude},{self.points.first().longitude}&destination={self.points.last().latitude},{self.points.last().longitude}"
    
    def get_points(self):
        return self.points.all()
    
    class Meta:
        ordering = ['route']
        
