from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers as rest_serializers
from rest_framework_gis.fields import GeometryField

from geotrek.feedback import models as feedback_models


class ReportActivityGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="label")

    class Meta:
        model = feedback_models.ReportActivity
        fields = ("id", "name")


class ReportCategoryGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="label")

    class Meta:
        model = feedback_models.ReportCategory
        fields = ("id", "name")


class ReportProblemMagnitudeGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="label")

    class Meta:
        model = feedback_models.ReportProblemMagnitude
        fields = ("id", "name")


class ReportStatusGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="label")

    class Meta:
        model = feedback_models.ReportStatus
        fields = ("id", "name")


class ReportSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    email = rest_serializers.CharField()
    activity = rest_serializers.SlugRelatedField("label", read_only=True)
    category = rest_serializers.SlugRelatedField("label", read_only=True)
    problem_magnitude = rest_serializers.SlugRelatedField("label", read_only=True)
    status = rest_serializers.SlugRelatedField("label", read_only=True)
    eid = rest_serializers.CharField(source="name_display")
    color = rest_serializers.CharField(source="status.color")

    class Meta:
        model = feedback_models.Report
        fields = "__all__"


class ReportGeojsonSerializer(MapentityGeojsonModelSerializer):
    name = rest_serializers.CharField()
    color = rest_serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = feedback_models.Report
        fields = ["id", "name", "color"]


class ReportGTAMSerializer(rest_serializers.ModelSerializer):
    geom = GeometryField(precision=7, transform=settings.API_SRID)

    # read-only
    activity = ReportActivityGTAMSerializer(read_only=True)
    category = ReportCategoryGTAMSerializer(read_only=True)
    problem_magnitude = ReportProblemMagnitudeGTAMSerializer(read_only=True)
    status = ReportStatusGTAMSerializer(read_only=True)

    # write-only
    activity_id = rest_serializers.PrimaryKeyRelatedField(
        source="activity",
        write_only=True,
        allow_null=True,
        queryset=feedback_models.ReportActivity.objects.all(),
    )
    category_id = rest_serializers.PrimaryKeyRelatedField(
        source="category",
        write_only=True,
        allow_null=True,
        queryset=feedback_models.ReportCategory.objects.all(),
    )
    problem_magnitude_id = rest_serializers.PrimaryKeyRelatedField(
        source="problem_magnitude",
        write_only=True,
        allow_null=True,
        queryset=feedback_models.ReportProblemMagnitude.objects.all(),
    )
    status_id = rest_serializers.PrimaryKeyRelatedField(
        source="status",
        write_only=True,
        allow_null=True,
        queryset=feedback_models.ReportStatus.objects.all(),
    )

    class Meta:
        model = feedback_models.Report
        fields = [
            "id",
            "date_insert",
            "date_update",
            "email",
            "comment",
            "geom",
            # read-only
            "activity",
            "category",
            "problem_magnitude",
            "status",
            # write-only
            "activity_id",
            "category_id",
            "problem_magnitude_id",
            "status_id",
        ]
        geo_field = "geom"


class ReportActivitySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportActivity
        fields = ["id", "label"]


class ReportCategorySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportCategory
        fields = ["id", "label"]


class ReportProblemMagnitudeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportProblemMagnitude
        fields = ["id", "label"]
