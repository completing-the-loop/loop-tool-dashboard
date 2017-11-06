from rest_framework.serializers import CharField
from rest_framework.serializers import DateField
from rest_framework.serializers import DecimalField
from rest_framework.serializers import DictField
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
        fields = ('id','lms_user_id', 'firstname', 'lastname', 'role', 'pageviews')


class CoursePagesetAndTotalsSerializer(Serializer):
    class PageSerializer(ModelSerializer):
        weeks = ListField()
        total = IntegerField()
        percent = DecimalField(max_digits=7, decimal_places=4)

        class Meta:
            model = Page
            fields = ('id', 'title', 'parent_id', 'content_type', 'weeks', 'total', 'percent')

    page_set = PageSerializer(many=True)
    totals_by_week = ListField(child=IntegerField())


class AssessmentUsersAndGradesSerializer(Serializer):
    class UserAndGradesSerializer(Serializer):
        class PkAndGradeDictField(DictField):
            pk = IntegerField()
            grade = DecimalField(max_digits=7, decimal_places=4)

        pk = IntegerField()
        name = CharField()
        grades = ListField(child=PkAndGradeDictField())

    class PkAndTitleSerializer(Serializer):
        pk = IntegerField()
        s = CharField()

    assessments = PkAndTitleSerializer(many=True)
    users = UserAndGradesSerializer(many=True)


class StudentsetAndTotalsSerializer(Serializer):
    class StudentSerializer(ModelSerializer):
        weeks = ListField()
        total = IntegerField()
        percent = DecimalField(max_digits=7, decimal_places=4)

        class Meta:
            model = LMSUser
            fields = ('id', 'fullname', 'weeks', 'total', 'percent')

    student_set = StudentSerializer(many=True)
    totals_by_week = ListField(child=IntegerField())
    highest_cell_value = IntegerField()


class StudentsetAndHighestSerializer(Serializer):
    class StudentSerializer(ModelSerializer):
        weeks = ListField()

        class Meta:
            model = LMSUser
            fields = ('id', 'fullname', 'weeks')

    student_set = StudentSerializer(many=True)
    highest_cell_value = IntegerField()


class CourseEventSerializer(ModelSerializer):
    weeks = ListField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'weeks')


class CourseContentPageEventSerializer(ModelSerializer):
    weeks = ListField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'parent_id', 'content_type', 'weeks')


class TopAccessedContentSerializer(ModelSerializer):
    pageviews = IntegerField()
    userviews = IntegerField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'userviews', 'pageviews')


class TopCommunicationAccessSerializer(ModelSerializer):
    pageviews = IntegerField()
    userviews = IntegerField()
    posts = IntegerField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'userviews', 'pageviews', 'posts')


class TopAssessmentAccessSerializer(ModelSerializer):
    userviews = IntegerField()
    average_score = DecimalField(max_digits=7, decimal_places=4)
    attempts = IntegerField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'userviews', 'average_score', 'attempts')


class DailyPageVisitsSerializer(Serializer):
    day = DateField()
    content_visits = IntegerField()
    communication_visits = IntegerField()
    assessment_visits = IntegerField()
    single_events = ListField()
    submission_events = ListField()


class WeeklyPageVisitsSerializer(Serializer):
    day = DateField()
    content_visits = IntegerField()
    communication_visits = IntegerField()
    assessment_visits = IntegerField()
    unique_visits = IntegerField()
    repeating_events = ListField()


class WeeklyMetricsSerializer(Serializer):
    day = DateField()
    unique_visits = IntegerField()
    students = IntegerField()
    sessions = IntegerField()
    avg_session_duration = IntegerField()
    avg_session_pageviews = IntegerField()


class StudentCommunicationSerializer(ModelSerializer):
    user_views = IntegerField()
    posts = IntegerField()

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'user_views', 'posts')


class StudentAssessmentSerializer(ModelSerializer):
    user_views = IntegerField()
    attempts = IntegerField()
    average_score = DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        model = Page
        fields = ('id', 'title', 'content_type', 'user_views', 'attempts', 'average_score')


class StudentsSerializer(ModelSerializer):
    class Meta:
        model = LMSUser
        fields = ('id', 'firstname', 'lastname', 'role', 'email')
