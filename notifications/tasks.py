from celery import shared_task
from django.core.mail import send_mail
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance
from datetime import datetime, timedelta


@shared_task
def daily_attendance_reminder():
    students = Student.objects.all()
    for student in students:
        send_mail(
            'Daily Attendance Reminder',
            'This is a reminder to mark your attendance for today.',
            'admin@example.com',
            [student.email],
            fail_silently=False,
        )
    return f'Sent reminders to {students.count()} students.'


@shared_task
def grade_update_notification(student_id, course_name, grade):
    student = Student.objects.get(id=student_id)
    send_mail(
        'Grade Update Notification',
        f'Your grade for {course_name} has been updated to {grade}.',
        'admin@example.com',
        [student.email],
        fail_silently=False,
    )
    return f'Grade notification sent to {student.name}.'


@shared_task
def weekly_performance_summary():
    students = Student.objects.all()
    for student in students:
        # Example logic to compile attendance and grades
        grades = Grade.objects.filter(student=student)
        attendance = Attendance.objects.filter(student=student, date__gte=datetime.now() - timedelta(days=7))

        # Create a summary string or template
        summary = f"Weekly Performance Summary for {student.name}:\n"
        summary += f"Grades:\n" + "\n".join([f"{grade.course.name}: {grade.grade}" for grade in grades])
        summary += "\nAttendance:\n" + "\n".join([f"{att.date}: {att.status}" for att in attendance])

        send_mail(
            'Weekly Performance Report',
            summary,
            'admin@example.com',
            [student.email],
            fail_silently=False,
        )
    return f'Sent weekly performance summaries to {students.count()} students.'

