from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserData(AbstractUser):
  organization = models.ManyToManyField('OrganizationData', related_name='users')
  description = models.CharField(max_length=150, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class OrganizationData(models.Model):
  name = models.CharField(max_length=100)
  owner = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='organizations')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class OrganizationPermissionData(models.Model):
  PERMISSION_TYPE = (
    ('shop', 'shop'),
    ('news', 'news'),
    ('menu', 'menu'),
    ('event', 'event'),
    ('band', 'band'),
    ('karaoke', 'karaoke'),
    ('post', 'post'),
    ('inspection', 'inspection'),
  )
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='organization_permissions')
  permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class OrganizationPermissionInspectionData(models.Model):
  organization = models.OneToOneField(OrganizationPermissionData, on_delete=models.CASCADE, related_name='organization_permission_inspection')
  inspected = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

class PermissionData(models.Model):
  PERMISSION_TYPE = (
    ('admin', 'admin'),
    ('shop', 'shop'),
    ('news', 'news'),
    ('menu', 'menu'),
    ('event', 'event'),
    ('band', 'band'),
    ('karaoke', 'karaoke'),
    ('post', 'post'),
    ('invite_user', 'invite_user'),
    ('inspection', 'inspection'),
  )
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='permissions')
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='permissions')
  permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class NewsData(models.Model):
  title = models.CharField(max_length=100)
  detail = models.TextField()
  show_top = models.BooleanField(default=False)
  important = models.BooleanField(default=False)
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='news')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='news', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class NewsImageData(models.Model):
  image = models.URLField()
  news = models.ForeignKey(NewsData, on_delete=models.CASCADE, related_name='images')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class NewsInspectionData(models.Model):
  news = models.OneToOneField(NewsData, on_delete=models.CASCADE, related_name='news_inspections')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='news_inspections', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class EventData(models.Model):
  title = models.CharField(max_length=100)
  place = models.CharField(max_length=100, null=True)
  detail = models.TextField()
  start = models.DateTimeField()
  end = models.DateTimeField()
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='events')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='events')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class EventImageData(models.Model):
  image = models.URLField()
  event = models.ForeignKey(EventData, on_delete=models.CASCADE, related_name='images')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class EventInspectionData(models.Model):
  event = models.OneToOneField(EventData, on_delete=models.CASCADE, related_name='event_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='event_inspections', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class ShopData(models.Model):
  name = models.CharField(max_length=100)
  address = models.CharField(max_length=100)
  detail = models.TextField()
  image = models.URLField(blank=True, null=True)
  organization = models.OneToOneField(OrganizationData, on_delete=models.CASCADE, related_name='shops')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='shops')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class ShopImageData(models.Model):
  image = models.URLField()
  shop = models.ForeignKey(ShopData, on_delete=models.CASCADE, related_name='images')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class ShopInspectionData(models.Model):
  shop = models.OneToOneField(ShopData, on_delete=models.CASCADE, related_name='shop_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='shop_inspections', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class MenuData(models.Model):
  name = models.CharField(max_length=100)
  price = models.IntegerField()
  shop = models.ForeignKey(ShopData, on_delete=models.CASCADE, related_name='menus')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='menus')
  sold_out = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class MenuInspectionData(models.Model):
  menu = models.OneToOneField(MenuData, on_delete=models.CASCADE, related_name='menu_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='menu_inspections', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class PostData(models.Model):
  title = models.CharField(max_length=100)
  detail = models.TextField()
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='posts', blank=True, null=True)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='posts')
  show = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class PostImageData(models.Model):
  image = models.URLField()
  post = models.ForeignKey(PostData, on_delete=models.CASCADE, related_name='images')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class PostInspectionData(models.Model):
  post = models.OneToOneField(PostData, on_delete=models.CASCADE, related_name='post_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='post_inspections', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class BandData(models.Model):
  name = models.CharField(max_length=100)
  detail = models.TextField()
  image = models.URLField(blank=True)
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='bands')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='bands')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class BandInspectionData(models.Model):
  band = models.OneToOneField(BandData, on_delete=models.CASCADE, related_name='band_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='band_inspections', blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

class BandSongData(models.Model):
  name = models.CharField(max_length=100)
  band = models.ForeignKey(BandData, on_delete=models.CASCADE, related_name='songs')
  spotify = models.URLField(blank=True)
  image = models.URLField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class BandSongInspectionData(models.Model):
  song = models.OneToOneField(BandSongData, on_delete=models.CASCADE, related_name='song_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='song_inspections', blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

class KaraokeData(models.Model):
  name = models.CharField(max_length=100)
  sing_user = models.CharField(max_length=100)
  spotify = models.URLField(blank=True)
  image = models.URLField(blank=True)
  organization = models.ForeignKey(OrganizationData, on_delete=models.CASCADE, related_name='karaokes')
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='karaokes')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class KaraokeInspectionData(models.Model):
  karaoke = models.OneToOneField(KaraokeData, on_delete=models.CASCADE, related_name='karaoke_inspection')
  inspected = models.BooleanField(default=False)
  ai = models.BooleanField(default=False)
  deleted = models.BooleanField(default=False)
  user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='karaoke_inspections', blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
