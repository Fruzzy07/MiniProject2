import logging
from rest_framework import viewsets
from .models import Grade
from .serializers import GradeSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsTeacher, IsAdmin, IsStudent
from drf_yasg.utils import swagger_auto_schema



logger = logging.getLogger('grades')


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Create a new grade for a student in a course",
        request_body=GradeSerializer,
        responses={201: GradeSerializer()},
        tags=['Grades']
    )
    def perform_create(self, serializer):
        student = serializer.validated_data['student']
        course = serializer.validated_data['course']
        teacher = self.request.user

        if course.instructor != teacher:
            raise PermissionDenied("You are not the instructor of this course.")

        logger.info(f'Grade created for student {student} in course {course} by teacher {teacher}')

        serializer.save(teacher=teacher)

    @swagger_auto_schema(
        operation_description="Retrieve a list of grades based on user role",
        responses={200: GradeSerializer(many=True)},
        tags=['Grades']
    )
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Grade.objects.filter(course__instructor=user)
        elif user.role == 'student':
            return Grade.objects.filter(student=user.student_profile)
        elif user.role == 'admin':
            return Grade.objects.all()
        return Grade.objects.none()

    @swagger_auto_schema(
        operation_description="Update a grade",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()},
        tags=['Grades']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a grade",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()},
        tags=['Grades']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)



