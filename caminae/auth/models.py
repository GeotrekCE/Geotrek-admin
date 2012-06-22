from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Structure(models.Model):
    name = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    structure = models.ForeignKey(Structure)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
