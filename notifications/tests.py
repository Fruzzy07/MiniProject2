from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core import mail
from notifications.tasks import daily_attendance_reminder, grade_update_notification, weekly_performance_summary
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance
from courses.models import Course, Enrollment  # Assuming you have a Course and Enrollment model
from datetime import datetime, timedelta

class NotificationTasksTestCase(TestCase):
    def setUp(self):

        User = get_user_model()

        self.instructor = User.objects.create_user(
            username='ismak_a',
            password='testpassword',
            email='adiko.instructor@example.com',
            first_name='Adilet',
            last_name='Ismak',
            role='teacher'
        )

        self.user = User.objects.create_user(
            username='johndoe',
            password='testpassword',
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

        self.course = Course.objects.create(
            name="Calculus 1",
            description="Introduction to Calculus",
            instructor=self.instructor
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
        )

        self.grade = Grade.objects.create(
            student=self.student,
            course=self.course,
            grade="A",
            teacher=self.instructor
        )

        self.attendance = Attendance.objects.create(
            student=self.student,
            course=self.course,
            status="Present"
        )

    def test_daily_attendance_reminder(self):
        # Call the task synchronously
        result = daily_attendance_reminder.apply()

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Daily Attendance Reminder', mail.outbox[0].subject)
        self.assertIn(self.student.email, mail.outbox[0].to)

        # Verify task result
        self.assertIn('Sent reminders to 1 students.', result.result)

    def test_grade_update_notification(self):
        result = grade_update_notification.apply(args=[self.student.id, 'Calculus 1', 'A'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Grade Update Notification', mail.outbox[0].subject)
        self.assertIn('Your grade for Calculus 1 has been updated to A', mail.outbox[0].body)

        self.assertIn(f'Grade notification sent to {self.student.name}.', result.result)

    def test_weekly_performance_summary(self):

        result = weekly_performance_summary.apply()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Weekly Performance Report', mail.outbox[0].subject)
        self.assertIn('Weekly Performance Summary for John Doe', mail.outbox[0].body)

        self.assertIn('Sent weekly performance summaries to 1 students.', result.result)


