from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Url(models.Model):
    user = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE)
    shorturl = models.CharField(max_length=10)
    originalurl = models.CharField(max_length=300)
    device = models.BooleanField(null=True)#PC=true, mobile=false
    browser = models.CharField(max_length=300)
    date_time_last_used = models.DateTimeField(auto_now=True)
