from rest_framework import serializers
from courses.models import Course, Enrollment
from students.models import Student

class CourseSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'instructor', 'course_name']

    def create(self, validated_data):
        # Добавляем инструктора из контекста запроса
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'enrollment_date']

    def validate(self, data):
        if Enrollment.objects.filter(student=data['student'], course=data['course']).exists():
            raise serializers.ValidationError("Этот студент уже зарегистрирован на данный курс.")

        request_user = self.context['request'].user
        if request_user.role == 'teacher' and data['course'].instructor != request_user:
            raise serializers.ValidationError("Вы можете регистрировать студентов только на курсы, которые вы преподаете.")

        return data
