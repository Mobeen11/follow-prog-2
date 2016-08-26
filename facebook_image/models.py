from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    STATUS = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    )
    status = models.CharField(max_length=255,
                              choices=STATUS, default=STATUS[0][0])
    author = models.OneToOneField(User, null=True, blank=True, related_name="user_profile")
    # author = models.ForeignKey(User, null=True, blank=True, related_name="user_profile")
    username = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField()
    new_profile_image = models.ImageField(blank=True, upload_to='profile_images')


    def __str__(self):
        return self.name

class FacebookStatus(models.Model):

    class Meta:
        verbose_name_plural = 'Facebook Statuses'
        ordering = ['publish_timestamp']

    STATUS = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    )
    status = models.CharField(max_length=255,
        choices=STATUS, default=STATUS[0][0])
    publish_timestamp = models.DateTimeField(null=True, blank=True)
    # author = models.ForeignKey(User)
    author = models.ForeignKey(User, null=True, blank=True, related_name="user_profile_facebook")
    message = models.TextField(max_length=255)
    link = models.URLField(null=True, blank=True)
    new_image = models.ImageField(blank=True, upload_to='facebookstatus_images')

    def __str__(self):
        return self.message

class ImagesList(models.Model):
    image = models.ImageField(blank=True,  upload_to='imageslist')
    # image_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.image)