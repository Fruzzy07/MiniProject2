import logging
from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsTeacher, IsAdmin
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger('attendance')


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    @swagger_auto_schema(
        operation_description="Create a new attendance record",
        request_body=AttendanceSerializer,
        responses={201: AttendanceSerializer()},
        tags=['Attendance']
    )

    def perform_create(self, serializer):
        teacher = self.request.user
        student = serializer.validated_data['student']
        course = serializer.validated_data['course']

        logger.info(f'Attendance marked for student {student} in course {course} by teacher {teacher}')

        serializer.save()



