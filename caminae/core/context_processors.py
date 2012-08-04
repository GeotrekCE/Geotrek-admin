from django.conf import settings as settings_ # import the settings file


def settings(context):
    return dict(
        TITLE=settings_.TITLE,
        DEBUG=settings_.DEBUG,
    )
