from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, MeSerializer
from drf_spectacular.utils import extend_schema

User = get_user_model()

class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user

@extend_schema(request=RegisterSerializer)
class RegisterView(APIView):

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('User created', status=201)
        