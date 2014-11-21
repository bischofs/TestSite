from django.db import models
from tastypie.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import BaseUserManager



# Create your models here.


