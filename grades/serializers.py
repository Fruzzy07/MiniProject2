# grades/serializers.py
from rest_framework import serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'teacher', 'student_name', 'course_name', 'teacher_name', 'date']

    def validate_grade(self, value):
        valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
        if value not in valid_grades:
            raise serializers.ValidationError(f"Grade must be one of {', '.join(valid_grades)}.")
        return value
