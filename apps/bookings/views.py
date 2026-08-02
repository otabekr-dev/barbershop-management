from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import BookingStatusSerializer, BookingSerializer
from apps.services.permissions import IsBarberOrAdmin
from .models import Booking

class BookingListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Booking.objects.all()
        elif user.role == "BARBER":
            return Booking.objects.filter(barber__user=user)
        else:
            return Booking.objects.filter(customer=user)


class BookingDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer 

class BookingStatusUpdateView(UpdateAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer           