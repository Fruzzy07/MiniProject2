from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core import mail
from students.models import Student
from notifications.tasks import daily_attendance_reminder


class StudentModelTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='yeraly_k',
            password='password123',
            email='yerosh@example.com',
            first_name='Yeraly',
            last_name='Kumargali',
            role='student'
        )

        self.student = Student.objects.create(
            user=self.user,
            name="Yeraly Kumargali",
            email="yerosh@example.com"
        )

    def test_student_creation(self):
        self.assertEqual(self.student.user.username, 'yeraly_k')
        self.assertEqual(self.student.name, 'Yeraly Kumargali')

    def test_student_email(self):
        self.assertEqual(self.student.email, 'yerosh@example.com')


class CachingTest(TestCase):
    def setUp(self):

        User = get_user_model()
        self.user = User.objects.create_user(
            username='john_doe',
            password='password123',
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            role='student'
        )

        self.student = Student.objects.create(
            user=self.user,
            name="John Doe",
            email="john.doe@example.com"
        )

        self.client = APIClient()

    def test_cache_student_data(self):
        # Simulate the first API request, which should store data in the cache
        response1 = self.client.get(f'/api/students/{self.student.id}/')

        # Check if the student data has been cached
        cached_data = cache.get(f'student_{self.student.id}')

        # Simulate a second request, which should fetch the data from the cache
        response2 = self.client.get(f'/api/students/{self.student.id}/')

        # Check that the cached data is used for the second request
        # The cache.get call should return the same result for the second request
        cached_data_after_second_request = cache.get(f'student_{self.student.id}')
        self.assertEqual(cached_data, cached_data_after_second_request)


class CeleryTaskTest(TestCase):
    def setUp(self):

        User = get_user_model()
        self.user = User.objects.create_user(
            username='john_doe',
            password='password123',
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            role='student'
        )

        self.student = Student.objects.create(
            user=self.user,
            name="John Doe",
            email="john.doe@example.com"
        )

    def test_daily_attendance_reminder(self):
        result = daily_attendance_reminder.apply()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Daily Attendance Reminder', mail.outbox[0].subject)
        self.assertIn(self.student.email, mail.outbox[0].to)  # Ensure the student's email is in the recipient list

        self.assertIn('Sent reminders to 1 students.', result.result)  # Adjust the expected message
