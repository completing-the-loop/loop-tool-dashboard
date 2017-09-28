from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer

from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit


class PageVisitSerializer(ModelSerializer):
    class Meta:
        model = PageVisit
        fields = '__all__' # TODO: Update this to specify exact fields to return


class TopCourseUsersSerializer(ModelSerializer):
    pageviews = IntegerField()

    class Meta:
        model = LMSUser
        fields = ('lms_user_id', 'firstname', 'lastname', 'role', 'pageviews')


class CommunicationAccessesPageSerializer(ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'weeks', 'total', 'percent')


class CommunicationAccessesSerializer(Serializer):
    page_set = CommunicationAccessesPageSerializer(many=True)
    totals_by_week = ListField(child=IntegerField())
