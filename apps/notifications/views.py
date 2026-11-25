from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsTelegramBot


from .serializers import TelegramLinkTokenSerializer, TelegramLinkVerifySerializer
from .service import create_telegram_link_token, verify_telegram_link_token


class TelegramLinkTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request:Request) -> Response:
        data = create_telegram_link_token(user=request.user)

        serializer = TelegramLinkTokenSerializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

class TelegramVerifyView(APIView):
    permission_classes = [IsTelegramBot]

    def post(self, request:Request) -> Response:
        serializer = TelegramLinkVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        telegram_id = serializer.validated_data['telegram_id']

        user = verify_telegram_link_token(
            raw_token=token, telegram_id=telegram_id
        )

        return Response(
            {
                'msg':'Telegram akkauntingiz muvaffaqiyatli bog\'landi.',
                'user_id':user.id
            },
            status=status.HTTP_200_OK
        )