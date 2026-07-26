from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]


    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Ro\'yxatdan o\'tdingiz', status=status.HTTP_201_CREATED)
        