from rest_framework import serializers
from .models import Attendance
from courses.models import Enrollment

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'course', 'date', 'status', 'student_name', 'course_name']

    def validate(self, data):
        request_user = self.context['request'].user

        if request_user.role == 'teacher':
            course = data['course']

            if course.instructor != request_user:
                raise serializers.ValidationError("Вы не можете отмечать посещаемость для курса, который вы не преподаете.")

            student = data['student']
            if not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("Этот студент не зарегистрирован на данный курс.")

        if request_user.role == 'admin':
            course = data['course']
            student = data['student']

            if not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("Этот студент не зарегистрирован на данный курс.")

        return data
