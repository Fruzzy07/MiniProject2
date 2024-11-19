from rest_framework import serializers
from .models import Student
from courses.models import  Enrollment
from grades.models import Grade
from attendance.models import Attendance


class StudentSerializer(serializers.ModelSerializer):
    enrolled_courses = serializers.SerializerMethodField()
    grades = serializers.SerializerMethodField()
    attendance_records = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'dob', 'registration_date', 'enrolled_courses', 'grades', 'attendance_records', 'user']

    def get_enrolled_courses(self, obj):
        courses = Enrollment.objects.filter(student=obj).values('course__name', 'course__description')
        return courses if courses else []

    def get_grades(self, obj):
        grades = Grade.objects.filter(student=obj).values('course__name', 'grade')
        return grades if grades else []  # Return an empty list if no grades are found

    def get_attendance_records(self, obj):
        attendance = Attendance.objects.filter(student=obj).values('course__name', 'date', 'status')
        return attendance if attendance else []
