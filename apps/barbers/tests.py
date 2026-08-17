from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Barber
from apps.services.models import Service
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class BarberTestCase(APITestCase):

    def setUp(self):
        self.barber_user = User.objects.create_user(username='barb', password='barbpass', role='BARBER')
        self.barber_profile = Barber.objects.create(user=self.barber_user, is_available=True)

        self.new_barber_user = User.objects.create_user(username='barb3', password='barb3pass', role='BARBER')

        self.another_barber_user = User.objects.create_user(username='barb2', password='barb2pass', role='BARBER')
        self.another_barber_profile = Barber.objects.create(user=self.another_barber_user, is_available=True)

        self.customer = User.objects.create_user(username='cust', password='custpass', role='CUSTOMER')

        self.admin = User.objects.create_user(username='adm', password='admpass', role='ADMIN')

        self.service = Service.objects.create(name='Tozalash', price=50000.0, duration='00:40:00')
            
    def test_create_barber_for_self(self):
        self.client.force_authenticate(user=self.new_barber_user)

        data = {
            'is_available': True
        }

        response = self.client.post(reverse('barber'), data=data, format='json')

        created = Barber.objects.get(pk=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.user, self.new_barber_user)

    def test_customer_unable_to_create_barber(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'is_available':True
        }

        response = self.client.post(reverse('barber'), data=data, format='json')



        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_change_another_barber_data(self):
        self.client.force_authenticate(user=self.barber_user)

        data = {
            "is_available":False
        }        

        response = self.client.patch(reverse('barber-detail', kwargs={'pk':self.another_barber_profile.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_able_to_change_any_barber_profile(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'is_available':False
        }

        response = self.client.patch(
            reverse('barber-detail', kwargs={'pk':self.another_barber_profile.pk}),
            data=data, format='json'
        )

        self.another_barber_profile.refresh_from_db()
        

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.another_barber_profile.is_available)

    def test_barber_can_update_own_availability(self):
        self.client.force_authenticate(user=self.barber_user)    

        data = {
            'is_available':False
        }

        response = self.client.patch(
            reverse('barber-availability', kwargs={'pk':self.barber_profile.pk}),
            data=data, format='json'
        )

        self.barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.barber_profile.is_available)

    def test_barber_cannot_update_others_availability(self):
        self.client.force_authenticate(user=self.barber_user)    

        data = {
            'is_available':False
        }

        response = self.client.patch(
            reverse('barber-availability', kwargs={'pk':self.another_barber_profile.pk}),
            data=data, format='json'
        )

        self.another_barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.barber_profile.is_available)

    def test_admin_can_update_any_availability(self):
        self.client.force_authenticate(user=self.admin)


        data = {
            'is_available': False
        }

        response = self.client.patch(
            reverse('barber-availability', kwargs={'pk':self.barber_profile.pk}),
            data=data, format='json'
        )

        self.barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.barber_profile.is_available)    


    def test_barber_can_assign_services_to_self(self):
        self.client.force_authenticate(user=self.barber_user)

        data = {
            'services': [self.service.id]
        }

        response = self.client.patch(
            reverse('barber-assign-service', kwargs={'pk':self.barber_profile.pk}),
            data=data, format='json'
        )

        self.barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.service, self.barber_profile.services.all())    

    def test_barber_cannot_assign_services_to_other(self):
        self.client.force_authenticate(user=self.barber_user)

        data = {
            'services': [self.service.id]
        }

        response = self.client.patch(
            reverse('barber-assign-service', kwargs={'pk':self.another_barber_profile.pk}),
            data=data, format='json'
        )

        self.another_barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(self.service, self.another_barber_profile.services.all())    


    def test_admin_can_assign_services_to_any(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'services': [self.service.id]
        }

        response = self.client.patch(
            reverse('barber-assign-service', kwargs={'pk':self.barber_profile.pk}),
            data=data, format='json'
        )

        self.barber_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.service, self.barber_profile.services.all())   