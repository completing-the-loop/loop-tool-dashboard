from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from olap.models import LMSUser
from olap.models import PageVisit


class PageVisitSerializer(ModelSerializer):
    class Meta:
        model = PageVisit
        fields = '__all__' # TODO: Update this to specify exact fields to return


class DimTopUserSerializer(ModelSerializer):
    pageviews = serializers.IntegerField()

    class Meta:
        model = LMSUser
        fields = ('lms_user_id', 'firstname', 'lastname', 'role', 'pageviews')
