from rest_framework.test import APITestCase, APIClient
from bicitaxi_api.api_v1.models import User

class BaseTestCase(APITestCase):
    user_creation_endpoint = "/api/v1/users/"

    def setUp(self):
        # We create the first user
        body = {
            "first_name": "Roberto",
            "last_name": "Franco",
            "email": "roberto@franzet.com",
            "password": "adminadmin",
            "profile": {
                "locale": "es"
            }
        }

        response = self.client.post(self.user_creation_endpoint, body, format='json')
        self.user = response.data