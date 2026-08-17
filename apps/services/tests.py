from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Service
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class ServiceTestCase(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='testing1', password='123456789', role='CUSTOMER')
        self.barber = User.objects.create_user(username='testing2', password='123456789', role='BARBER')
        self.admin = User.objects.create_user(username='testing3', password='123456789', role='ADMIN')

        self.existing_service = Service.objects.create(name='soqol olish', price=55000.0, duration='00:30:00')

    def test_customer_unable_create_service(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'name':'sname',
            'price':50000.0,
            'duration':'00:30:00'
        }

        response = self.client.post(reverse('services'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Service.objects.filter(name='sname').exists())


    def test_barber_create_service(self):
        self.client.force_authenticate(user=self.barber)

        data = {
            'name':'sname',
            'price':50000.0,
            'duration':'00:30:00'
        }

        response = self.client.post(reverse('services'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Service.objects.filter(name='sname').exists())

    def test_admin_create_service(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name':'snames',
            'price':50000.0,
            'duration':'00:30:00'
        }

        response = self.client.post(reverse('services'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Service.objects.filter(name='snames').exists())


    def test_duplicate_name(self):
        self.client.force_authenticate(user=self.barber)

        data = {
            'name':'soqol olish',
            'price':50000.0,
            'duration':'00:20:00'
        }    

        response = self.client.post(reverse('services'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Service.objects.filter(name='soqol olish').count(), 1)

    def test_case_insensitive_duplicate_name(self):
        self.client.force_authenticate(user=self.barber)

        data = {
            'name':'Soqol olish',
            'price':50000.0,
            'duration':'00:20:00'
        }    

        response = self.client.post(reverse('services'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Service.objects.filter(name='soqol olish').count(), 1)

    def test_update_service_without_changing_name(self):
        self.client.force_authenticate(user=self.barber)

        data = {
            'name': self.existing_service.name,
            'price': 60000.0,
            'duration':'00:15:00'
        }

        response = self.client.patch(reverse('services-detailed', kwargs={'pk':self.existing_service.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Service.objects.filter(name=f'{self.existing_service.name}').count(), 1)