from django.test import TestCase


class TestHelloWorld(TestCase):

    def test_hello_world(self):
        """
        Simple test case
        """
        self.assertEqual(1, 1)
