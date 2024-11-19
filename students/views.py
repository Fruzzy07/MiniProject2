import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsStudent, IsAdmin, IsTeacher
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger('students')

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsStudent | IsAdmin | IsTeacher]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'dob', 'registration_date']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'dob', 'registration_date']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsAdmin | IsStudent | IsTeacher]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsAdmin | IsStudent]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Retrieve a list of students based on the user role.",
        responses={200: StudentSerializer(many=True)},
        tags=['Students']
    )
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Student.objects.filter(user=user)
        elif user.role == 'teacher':
            course_ids = user.course_set.values_list('id', flat=True)
            return Student.objects.filter(enrollment__course__in=course_ids).distinct()
        elif user.role == 'admin':
            return Student.objects.all()
        return Student.objects.none()

    @swagger_auto_schema(
        operation_description="Create a new student profile. Requires admin permissions.",
        request_body=StudentSerializer,
        responses={201: StudentSerializer()},
        tags=['Students']
    )
    def perform_create(self, serializer):
        user_to_add = serializer.validated_data.get('user')

        if user_to_add is None:
            logger.error("No user provided to create a student profile.")
            raise ValidationError({"detail": "A user must be provided to create a student profile."})

        if Student.objects.filter(user=user_to_add).exists():
            logger.warning(f'Attempt to create duplicate student profile for user {user_to_add.username}')
            raise ValidationError({"detail": "User already has an associated student profile."})

        instance = serializer.save(user=user_to_add)
        logger.info(f'Student profile created for student {instance.name}')

    @swagger_auto_schema(
        operation_description="Update a student profile. Only admins or the student themselves can update.",
        request_body=StudentSerializer,
        responses={200: StudentSerializer()},
        tags=['Students']
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and request.user.role != 'admin':
            logger.warning(f'Unauthorized update attempt by user {request.user.username} for student profile {instance.name}')
            return Response({"detail": "You can only update your own profile."}, status=status.HTTP_400_BAD_REQUEST)

        response = super().update(request, *args, **kwargs)
        student_id = kwargs.get('pk')

        logger.info(f'Student profile updated for student {instance.name} by user {request.user.username}')

        cache.delete(f'student_profile_{student_id}')  # Invalidate cache on update
        return response

    @swagger_auto_schema(
        operation_description="Retrieve a student profile. Cached results may be used.",
        responses={200: StudentSerializer()},
        tags=['Students']
    )
    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        cache_key = f'student_profile_{student_id}'

        cached_profile = cache.get(cache_key)
        if cached_profile:
            logger.info(f'Cache hit for student profile {student_id}')
            return Response(cached_profile, status=status.HTTP_200_OK)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=1800)  # Cache the profile for 30 minutes

        logger.info(f'Student profile retrieved for student {response.data["name"]}')
        return response

    @swagger_auto_schema(
        operation_description="Delete a student profile. Admins can delete any profile.",
        responses={204: 'No content'},
        tags=['Students']
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        student_id = kwargs.get('pk')

        logger.info(f'Student profile deleted for student {instance.name} by user {request.user.username}')

        response = super().destroy(request, *args, **kwargs)
        cache.delete(f'student_profile_{student_id}')
        return response
