from django.contrib import admin

from geotrek.feedback import models as feedback_models


admin.site.register(feedback_models.ReportCategory)
