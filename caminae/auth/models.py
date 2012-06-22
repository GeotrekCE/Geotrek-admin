from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Structure(models.Model):
    name = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


def default_structure():
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    structure = models.ForeignKey(Structure, default=default_structure)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
