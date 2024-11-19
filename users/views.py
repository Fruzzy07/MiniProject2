import logging
from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserSerializer
from .models import CustomUser
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger('users')


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()


    @swagger_auto_schema(
        operation_description="Create a new user. Requires basic user registration details.",
        request_body=CustomUserCreateSerializer,
        responses={201: CustomUserCreateSerializer()},
        tags=['Users']
    )
    def perform_create(self, serializer):
        super().perform_create(serializer)

    def get_serializer_class(self):
        if self.action == 'create':
            logger.info(f'User creation initiated for {self.request.data.get("username")}')
            return CustomUserCreateSerializer
        return CustomUserSerializer


    @swagger_auto_schema(
        operation_description="Update a user's information.",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer()},
        tags=['Users']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a user profile. Admin permissions required.",
        responses={204: 'No content'},
        tags=['Users']
    )
    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'User deleted: {username}')
        return response

    @swagger_auto_schema(
        operation_description="Retrieve a list of all users.",
        responses={200: CustomUserSerializer(many=True)},
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



