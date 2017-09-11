from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from olap.models import DimUser
from olap.models import FactCourseVisit


class FactCourseVisitSerializer(ModelSerializer):
    class Meta:
        model = FactCourseVisit
        fields = '__all__' # TODO: Update this to specify exact fields to return


class DimTopUserSerializer(ModelSerializer):
    pageviews = serializers.IntegerField()

    class Meta:
        model = DimUser
        fields = ('lms_id', 'firstname', 'lastname', 'role', 'pageviews')
