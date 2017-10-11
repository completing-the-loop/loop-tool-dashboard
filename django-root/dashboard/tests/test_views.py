from django.test.testcases import TestCase
from django.urls import reverse

from dashboard.tests.factories import CourseOfferingFactory
from dashboard.tests.factories import LecturerFactory


class CourseListTestCase(TestCase):

    def setUp(self):
        self.lecturer_password = 'password'
        self.lecturer = LecturerFactory(password=self.lecturer_password)
        self.unowned_course = CourseOfferingFactory()
        self.owned_course = CourseOfferingFactory(owners=(self.lecturer,))

        self.login_url = reverse('dashboard:login')
        self.course_list_url = reverse('dashboard:course_list')

    def test_unauthorised_access(self):
        response = self.client.get(self.course_list_url, follow=True)

        login_with_next_url = '{}?next={}'.format(self.login_url, self.course_list_url)
        self.assertRedirects(response, login_with_next_url)

    def test_authorised_access(self):
        response = self.client.post(self.login_url, {'username': self.lecturer.email, 'password': self.lecturer_password}, follow=True)
        self.assertRedirects(response, self.course_list_url)

        self.assertIn(self.owned_course, response.context['courses'])
        self.assertNotIn(self.unowned_course, response.context['courses'])

