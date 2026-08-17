from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class RegisterTestCase(APITestCase):

    def setUp(self):
        self.valid_data = {
            'username':'testname',
            'first_name':'1sttest',
            'last_name':'lasttest',
            'email':'test@example.com',
            'password':'SuperDuperPass',
            'confirm':'SuperDuperPass'
        }

    def test_register_success(self):
        data = self.valid_data.copy()
        response = self.client.post(reverse('register'), data=data, format='json')


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testname').exists())

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data['confirm'] = 'DifferentPass'


        response = self.client.post(reverse('register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username=data['username']).exists())

    def test_duplicate_username(self):
        user = User.objects.create_user(
            username='zuck',
            first_name='zuck',
            last_name='zucker',
            password='zuckpass',
            email='tezt@gmail.com'
        )

        data = self.valid_data.copy()
        data['username'] = 'zuck'

        response = self.client.post(reverse('register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(username='zuck').count(), 1)        

class LoginTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(
            email ='test11@example.com',
            username = 'testing_user',
            password = 'Very_Strong_Pass'
        )

    def test_login_success(self):
        data = {
            'username':'testing_user',
            'password': 'Very_Strong_Pass'
        }

        response = self.client.post(reverse('login'), data=data, format='json')


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)            

    def test_incorrect_password(self):
        data = {
            'username':'testing_user',
            'password':'VVery_strong_ppp'
        }    

        response = self.client.post(reverse('login'), data=data, format='json')


        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_user_existence(self):
        data = {
            'username':'ttesstt',
            'password':'Very_Strong_Pass'
        }

        response = self.client.post(reverse('login'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)    