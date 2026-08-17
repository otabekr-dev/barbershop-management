from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import BookingStatusSerializer, BookingSerializer
from apps.services.permissions import IsBarberOrAdmin
from .models import Booking
from .permissions import IsBookingOwner, IsBookingParticipantOrAdmin, IsAssignedBarberOrAdmin

WORK_START = "08:00"
WORK_END = "18:00"
SLOT_DURATION = 30


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
    permission_classes = [IsBookingParticipantOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer 

class BookingStatusUpdateView(UpdateAPIView):
    permission_classes = [IsAssignedBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer           


class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get(self, request: Request, pk:int) -> Response:
        date = datetime.strptime(request.query_params.get('date'), "%Y-%m-%d").date()

        available_slots = []

        work_start = datetime.strptime(WORK_START, "%H:%M").time()
        work_end = datetime.strptime(WORK_END, "%H:%M").time()

        current = datetime.combine(date, work_start)
        end_of_day = datetime.combine(date, work_end)

        existing_books = Booking.objects.filter(barber_id=pk, date=date).exclude(status='CANCELLED')

        while current < end_of_day:
            is_busy = False
            for booking in existing_books:
                booking_start = datetime.combine(booking.date, booking.start_time)
                booking_end = booking_start + booking.service.duration

                if booking_start <= current < booking_end:
                    is_busy = True
                    break


            if not is_busy:
                available_slots.append(current.strftime("%H:%M"))

            current += timedelta(minutes=30)
        return Response(available_slots, status=status.HTTP_200_OK)                    


class CancelAppointmentView(UpdateAPIView):
    permission_classes = [IsBookingOwner]
    authentication_classes = [JWTAuthentication]
    serializer_class = BookingStatusSerializer
    queryset = Booking.objects.all()


    def perform_update(self, serializer):
            serializer.save(status='CANCELLED')