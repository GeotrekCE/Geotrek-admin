from django.contrib.auth import get_user_model


def create_user_profile(sender, instance, created, **kwargs):
    from geotrek.authent.models import UserProfile
    if not created:
        return
    if sender != get_user_model():
        return
    UserProfile.objects.create(user=instance)
