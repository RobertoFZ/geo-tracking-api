from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from bicitaxi_api.api_v1.models import User


class UserTestCase(APITestCase):
    creation_endpoint = "/api/v1/users/"
    user = None

    def test_user(self):
        self.create_user()
        self.update_user()
    

    def create_user(self):
        body = {
            "first_name": "Roberto",
            "last_name": "Franco",
            "email": "roberto@franzet.com",
            "password": "adminadmin",
            "profile": {
                "locale": "es"
            }
        }

        response = self.client.post(self.creation_endpoint, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'roberto@franzet.com')
        self.user = response.data

    def update_user(self):
        body = {
            "id": self.user['id'],
            "first_name": self.user['first_name'],
            "last_name": self.user['last_name'],
            "email": self.user['email'],
            "password": self.user['password'],
            "profile": {
                "locale": "en"
            }
        }
        update_endpoint = "/api/v1/users/%s" % self.user['id']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % self.user['token'])
        response = client.put(update_endpoint, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['locale'], body['profile']['locale'])