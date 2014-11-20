from django.db import models
from tastypie.utils.timezone import now
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.user.username
        
    @receiver(post_save, sender=User)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            UserProfile.objects.get_or_create(user=instance)
                
    


# Create your models here.


