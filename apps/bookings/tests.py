from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.barbers.models import Barber
from apps.services.models import Service
from django.contrib.auth import get_user_model
from .models import Booking
from datetime import timedelta, date

User = get_user_model()


class BookingTestCase(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='cusername', password='cusespass', role='CUSTOMER')
        self.barber_user = User.objects.create_user(username='busername', password='barspass', role='BARBER')
        self.barber_user2 = User.objects.create_user(username='busername2', password='barspass', role='BARBER')
        self.admin = User.objects.create_user(username='adusername', password='adspasss', role='ADMIN')

        self.customer2 = User.objects.create_user(username='cusername2', password='cusespass2', role='CUSTOMER')


        self.barber_profile = Barber.objects.create(user=self.barber_user, is_available=True)
        self.barber_profile2 = Barber.objects.create(user=self.barber_user2, is_available=True)

        self.service = Service.objects.create(name='sername', price=150000.0, duration='00:30:00')

        self.future_date = (date.today() + timedelta(days=1))

        
    def test_create_booking_success(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'barber':self.barber_profile.id,
            'service':self.service.id,
            'date': str(self.future_date),
            'start_time':'10:00:00'
        }


        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)    

    def test_barber_self_booking(self):
        self.client.force_authenticate(user=self.barber_user)


        data = {
            'barber':self.barber_profile.id,
            'service':self.service.id,
            'date': str(self.future_date),
            'start_time': '10:00:00'
        }        

        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("O'zingizga booking qila olmaysiz", str(response.data))
        self.assertEqual(Booking.objects.count(), 0)

    def test_same_slot_overlap(self):
        self.client.force_authenticate(user=self.customer)
        
        existing_booking = Booking.objects.create(
            customer=self.customer2 ,barber=self.barber_profile, service=self.service,
            date=self.future_date, start_time='10:00:00', status='PENDING'
        )

        data = {
            'barber':self.barber_profile.id,
            'service':self.service.id,
            'date': str(self.future_date),
            'start_time': '10:00:00'
        }

        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertIn('Bu vaqt oralig\'ida sartarosh band', str(response.data))

    def test_partial_overlap(self):
        self.client.force_authenticate(user=self.customer)
        
        existing_booking = Booking.objects.create(
            customer=self.customer2 ,barber=self.barber_profile, service=self.service,
            date=self.future_date, start_time='10:00:00', status='PENDING'
        )

        data = {
            'barber':self.barber_profile.id,
            'service':self.service.id,
            'date': str(self.future_date),
            'start_time': '10:15:00'
        }

        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertIn('Bu vaqt oralig\'ida sartarosh band', str(response.data))

    def test_no_overlap_adjacent_time(self):
        self.client.force_authenticate(user=self.customer)
        
        existing_booking = Booking.objects.create(
            customer=self.customer2 ,barber=self.barber_profile, service=self.service,
            date=self.future_date, start_time='10:00:00', status='PENDING'
        )

        data = {
            'barber':self.barber_profile.id,
            'service':self.service.id,
            'date': str(self.future_date),
            'start_time': '10:30:00'
        }

        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)

    def test_no_overlap_different_barber(self):
        self.client.force_authenticate(user=self.customer)

        existing_booking = Booking.objects.create(
            customer=self.customer2 ,barber=self.barber_profile, service=self.service,
            date=self.future_date, start_time='10:00:00', status='PENDING'
        )

        data = {
            'barber':self.barber_profile2.id,
            'service':self.service.id,
            'date':self.future_date,
            'start_time':'10:00:00'
        }

        response = self.client.post(reverse('booking'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)        

    def test_customer_cannot_view_others_booking(self):
        self.client.force_authenticate(user=self.customer2)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )

        response = self.client.get(reverse('booking-details', kwargs={'pk':booking.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_customer_can_view_own_booking(self):                
        self.client.force_authenticate(user=self.customer)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )

        response = self.client.get(reverse('booking-details', kwargs={'pk':booking.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_barber_can_view_assigned_booking(self):
        self.client.force_authenticate(self.barber_user)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )

        response = self.client.get(reverse('booking-details', kwargs={'pk':booking.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_barber_cannot_view_others_booking(self):
        self.client.force_authenticate(self.barber_user)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile2,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )

        response = self.client.get(reverse('booking-details', kwargs={'pk':booking.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_barber_can_update_status(self):
        self.client.force_authenticate(user=self.barber_user)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )
        
        data = {
            'status':'CONFIRMED'
        }

        response = self.client.patch(reverse('booking-status-update', kwargs={'pk':booking.id}), data=data, format='json')

        booking.refresh_from_db()

        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_barber_cannot_update_status(self):
        self.client.force_authenticate(user=self.barber_user)

        booking = Booking.objects.create(
            customer=self.customer, barber=self.barber_profile2,
            service=self.service, date=self.future_date,
            start_time='10:00:00', status='PENDING'
        )
        
        data = {
            'status':'CONFIRMED'
        }

        response = self.client.patch(reverse('booking-status-update', kwargs={'pk':booking.id}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)