import logging
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin, IsTeacher, IsStudent
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema



logger = logging.getLogger('courses')


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'instructor']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date']

    def get_permissions(self):
        if self.action in ['create', 'list', 'update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Create a new course",
        request_body=CourseSerializer,
        responses={201: CourseSerializer()},
        tags=['Courses']
    )

    def perform_create(self, serializer):
        course_name = serializer.validated_data['name']
        if self.request.user.role not in ['teacher', 'admin']:
            logger.warning(f'Unauthorized create attempt by user {self.request.user.username}')
            raise PermissionDenied("Only teachers and admins can create courses.")
        logger.info(f'Course {course_name} created by user {self.request.user.username}')
        serializer.save(instructor=self.request.user)

    @swagger_auto_schema(
        operation_description="List all courses",
        responses={200: CourseSerializer(many=True)},
        tags=['Courses']
    )

    def list(self, request, *args, **kwargs):
        cached_courses = cache.get('course_list')
        if cached_courses:
            logger.info('Cache hit for course list')
            return Response(cached_courses, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set('course_list', response.data, timeout=3600)
        logger.info('Course list retrieved from database and cached')
        return response

    @swagger_auto_schema(
        operation_description="Update a course",
        request_body=CourseSerializer,
        responses={200: CourseSerializer()},
        tags=['Courses']
    )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete('course_list')  # Invalidate cache on update
        logger.info(f'Course updated with ID {kwargs["pk"]}')
        return response

    @swagger_auto_schema(
        operation_description="Delete a course",
        responses={204: 'No content'},
        tags=['Courses']
    )

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.delete('course_list')
        logger.info(f'Course deleted with ID {kwargs["pk"]}')
        return response


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    @swagger_auto_schema(
        operation_description="Create a new enrollment",
        request_body=EnrollmentSerializer,
        responses={201: EnrollmentSerializer()},
        tags=['Enrollments']
    )

    def perform_create(self, serializer):
        request_user = self.request.user
        course = serializer.validated_data['course']
        student = serializer.validated_data['student']


        logger.info(f'Enrollment created for student {student.name} in course {course.name}')

        if request_user.role == 'teacher' and course.instructor != request_user:
            logger.warning(f'Unauthorized enrollment attempt by user {request_user.username} in course {course.id}')
            raise PermissionDenied("You can only enroll students in your own courses.")

        serializer.save()

