import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from customer import models


class CustomerViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_data = {
            'sex_tape': 'Male',
            'dni': 123456789,
            'birth_date': '2000-01-01T00:00:00Z',
            'user': {
                'email': 'test@example.com',
                'name': 'Lucho',
                'last_name': 'Corradini',
            }
        }
        user = models.CustomerUser.objects.create(**self.customer_data.pop('user'))
        self.customer = models.Customer.objects.create(id=1000, user=user, **self.customer_data)
        self.user = None
        self.token = None


    def authenticate_api(self):
        user_data = {
            'username': 'testuser4',
            'password': 'testpassword',
            'email': 'test4@example.com',
            'first_name': 'Lucho',
            'last_name': 'Corradini'
        }
        self.user = User.objects.create_user(**user_data)
        self.token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def tearDown(self):
        if (self.token and self.user):
            Token.objects.filter(key=self.token.key).delete()
            User.objects.filter(id=self.user.id).delete()
            self.client.credentials(HTTP_AUTHORIZATION=None)

    def create_customers(self):
        customers_data = [
            {
                'sex_tape': 'Male',
                'dni': 123456799,
                'birth_date': '2000-01-01T00:00:00Z',
                'user': {'email': 'test1@example.com', 'name': 'lucho1', 'last_name': 'Corradini1'}
            },
            {
                'sex_tape': 'Male',
                'dni': 987654321,
                'birth_date': '2000-01-01T00:00:00Z',
                'user': {'email': 'test2@example.com', 'name': 'lucho2', 'last_name': 'Corradini2'}
            },
        ]

        to_create = []

        for index, customer_data in enumerate(customers_data):
            data = customer_data.pop('user')
            user = models.CustomerUser.objects.create(**data)
            customer = models.Customer(id=index+100, user=user, **customer_data)
            to_create.append(customer)

        models.Customer.objects.bulk_create(to_create)

    def test_retrieve_customer_status_200(self):
        self.authenticate_api()
        response = self.client.get('/api/v1/customer/1000')
        customer = models.Customer.objects.first()

        response_expected = {
            "wallet_id": str(customer.wallet_id),
            "sex_tape": "Male",
            "dni": 123456789,
            "birth_date": "2000-01-01T00:00:00Z",
            "created_at": customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user": {
                "email": "test@example.com",
                "name": "Lucho",
                "last_name": "Corradini"
            }
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_customer_status_404(self):
        self.authenticate_api()
        response = self.client.get('/api/v1/customer/2')

        response_expected = {
            "detail": "Not found."
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_customer_status_401_authentication_not_provider(self):
        response = self.client.get('/api/v1/customer/1000')

        response_expected = {
            "detail": "Authentication credentials were not provided."
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_customer_status_401_with_invalid_token(self):
        invalid_token = "b2facc0e0dc81603ba101201e85eea8483eb0dff"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + invalid_token)
        response = self.client.get('/api/v1/customer/1000')

        response_expected = {
            "detail": "Invalid token"
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_customers_status_200(self):
        self.create_customers()
        self.authenticate_api()
        response = self.client.get('/api/v1/customer/')
        customers = models.Customer.objects.all().order_by('created_at')

        response_expected = {
            "count": customers.count(),
            "next": None,
            "previous": None,
            "results": []
        }

        for customer in customers:
            customer_data = {
                'wallet_id': str(customer.wallet_id),
                'sex_tape': customer.sex_tape,
                'dni': customer.dni,
                'birth_date': customer.birth_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'user': {
                    'email': customer.user.email,
                    'name': customer.user.name,
                    'last_name': customer.user.last_name
                }
            }
            response_expected["results"].append(customer_data)

        response_data_json = json.loads(json.dumps(response.data))
        self.assertDictEqual(response_data_json, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_list_customers_status_200_with_pagination(self):
        self.create_customers()
        self.authenticate_api()
        offset = 2
        size = 1
        response = self.client.get('/api/v1/customer/', { 'page': offset, 'limit': size })
        customers = models.Customer.objects.all().order_by('created_at')
        
        response_expected = {
            "count": customers.count(),
            "next": 'http://testserver/api/v1/customer/?limit=1&page=3',
            "previous": 'http://testserver/api/v1/customer/?limit=1',
            "results": []
        }

        page = []
        pages =  []
        content = []

        for customer in customers:
            if len(content) == size:
                pages.append(content)
                content = []
            content.append(customer)
        
        if len(content) > 0:
            pages.append(content)

        if len(pages) >= offset:
            page = pages[offset -1]

        for customer in page:
            customer_data = {
                'wallet_id': str(customer.wallet_id),
                'sex_tape': customer.sex_tape,
                'dni': customer.dni,
                'birth_date': customer.birth_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'user': {
                    'email': customer.user.email,
                    'name': customer.user.name,
                    'last_name': customer.user.last_name
                }
            }
            response_expected["results"].append(customer_data)

        response_data_json = json.loads(json.dumps(response.data))
        self.assertDictEqual(response_data_json, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_customers_status_200_with_sorting(self):
        self.create_customers()
        self.authenticate_api()
        sort_param = '-dni'
        response = self.client.get('/api/v1/customer/', { 'sortBy': sort_param })
        customers = models.Customer.objects.all().order_by(sort_param)

        response_expected = {
            "count": customers.count(),
            "next": None,
            "previous": None,
            "results": []
        }

        for customer in customers:
            customer_data = {
                'wallet_id': str(customer.wallet_id),
                'sex_tape': customer.sex_tape,
                'dni': customer.dni,
                'birth_date': customer.birth_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'user': {
                    'email': customer.user.email,
                    'name': customer.user.name,
                    'last_name': customer.user.last_name
                }
            }
            response_expected["results"].append(customer_data)

        response_data_json = json.loads(json.dumps(response.data))
        self.assertDictEqual(response_data_json, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_customers_status_200_with_filter(self):
        self.create_customers()
        self.authenticate_api()
        filter_param = { 'user__email': 'test2@example.com' }
        response = self.client.get('/api/v1/customer/', filter_param)

        customers = models.Customer.objects.filter(**filter_param).order_by('created_at')

        response_expected = {
            "count": customers.count(),
            "next": None,
            "previous": None,
            "results": []
        }

        for customer in customers:
            customer_data = {
                'wallet_id': str(customer.wallet_id),
                'sex_tape': customer.sex_tape,
                'dni': customer.dni,
                'birth_date': customer.birth_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'user': {
                    'email': customer.user.email,
                    'name': customer.user.name,
                    'last_name': customer.user.last_name
                }
            }
            response_expected["results"].append(customer_data)

        response_data_json = json.loads(json.dumps(response.data))
        self.assertDictEqual(response_data_json, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_customer_status_401_authentication_not_provider(self):
        response = self.client.get('/api/v1/customer/')

        response_expected = {
            "detail": "Authentication credentials were not provided."
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_customer_status_401_with_invalid_token(self):
        invalid_token = "b2facc0e0dc81603ba101201e85eea8483eb0dff"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + invalid_token)
        response = self.client.get('/api/v1/customer/')

        response_expected = {
            "detail": "Invalid token"
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customer_status_201(self):
        self.maxDiff = None
        self.authenticate_api()

        body = {
            "sex_tape": "Male",
            "dni": 33323773,
            "birth_date": "1987-10-13T01:14:14Z",
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        response = self.client.post('/api/v1/customer/', body, format='json')
        customer = models.Customer.objects.filter(dni=body['dni']).first()

        response_expected = {
            "wallet_id": customer and str(customer.wallet_id),
            "sex_tape": "Male",
            "dni": 33323773,
            "birth_date": "1987-10-13T01:14:14Z",
            "created_at": customer and customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        customer_exists = models.Customer.objects.filter(dni=body['dni']).exists()

        self.assertTrue(customer_exists)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_customer_status_400_without_params(self):
        self.authenticate_api()

        all_customers_before = models.Customer.objects.all().count()
        body = {}

        response = self.client.post('/api/v1/customer/', body, format='json')

        response_expected = {
            "sex_tape": [
                "This field is required."
            ],
            "dni": [
                "This field is required."
            ],
            "birth_date": [
                "This field is required."
            ],
            "user": [
                "This field is required."
            ]
        }

        all_customers_expected = models.Customer.objects.all().count()

        self.assertEqual(all_customers_before, all_customers_expected)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_status_400_customer_already_exists(self):
        self.authenticate_api()

        body = {
            "sex_tape": "Male",
            "dni": 123456789,
            "birth_date": "1987-10-13T01:14:14Z",
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        # Customer exists before do request
        c_exists = models.Customer.objects.filter(dni=body['dni']).exists()

        response = self.client.post('/api/v1/customer/', body, format='json')

        response_expected = {
            "dni": [
                "customer with this dni already exists."
            ]
        }

        # Customer exists after do request
        c2_exists = models.Customer.objects.filter(dni=body['dni']).exists()

        self.assertEqual(c_exists, c2_exists)
        self.assertTrue(c2_exists)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_customer_status_401_authentication_not_provider(self):
        response = self.client.post('/api/v1/customer/')

        response_expected = {
            "detail": "Authentication credentials were not provided."
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customer_status_401_with_invalid_token(self):
        invalid_token = "b2facc0e0dc81603ba101201e85eea8483eb0dff"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + invalid_token)
        response = self.client.post('/api/v1/customer/')

        response_expected = {
            "detail": "Invalid token"
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customer_status_200(self):
        self.maxDiff = None
        self.authenticate_api()

        body = {
            "sex_tape": "Male",
            "dni": 123456789,
            "birth_date": "1987-10-13T01:14:14Z",
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        response = self.client.put('/api/v1/customer/1000', body, format='json')

        customer = models.Customer.objects.filter(dni=body['dni']).first()

        response_expected = {
            "wallet_id": customer and str(customer.wallet_id),
            "sex_tape": "Male",
            "dni": 123456789,
            "birth_date": "1987-10-13T01:14:14Z",
            "created_at": customer and customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        customer_exists = models.Customer.objects.filter(dni=body['dni']).exists()

        self.assertTrue(customer_exists)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_customer_status_400_customer_user_already_exists(self):
        self.authenticate_api()
        self.create_customers()

        body = {
            "sex_tape": "Male",
            "dni": 33323773,
            "birth_date": "1987-10-13T01:14:14Z",
            "user": {
                "email": "test1@example.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        response = self.client.put('/api/v1/customer/1000', body, format='json')

        customer = models.Customer.objects.filter(dni=body['dni']).first()

        response_expected = {
            "user": {
                "email": "User with this email already exists."
            }
        }

        customer_exists = models.CustomerUser.objects.filter(email=body['user']['email']).exists()

        self.assertTrue(customer_exists)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_status_400_customer_already_exists(self):
        self.authenticate_api()
        self.create_customers()

        body = {
            "sex_tape": "Male",
            "dni": 987654321,
            "birth_date": "1987-10-13T01:14:14Z",
            "user": {
                "email": "luciano.j.corradini1@gmail.com",
                "name": "Luciano",
                "last_name": "Corradini"
            }
        }

        response = self.client.put('/api/v1/customer/1000', body, format='json')

        response_expected = {
            "dni": [
                "customer with this dni already exists."
            ]
        }

        customer_exists = models.Customer.objects.filter(dni=body['dni']).exists()

        self.assertTrue(customer_exists)
        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_status_401_authentication_not_provider(self):
        response = self.client.put('/api/v1/customer/1')

        response_expected = {
            "detail": "Authentication credentials were not provided."
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customer_status_401_with_invalid_token(self):
        invalid_token = "b2facc0e0dc81603ba101201e85eea8483eb0dff"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + invalid_token)
        response = self.client.put('/api/v1/customer/1')

        response_expected = {
            "detail": "Invalid token"
        }

        self.assertDictEqual(response.data, response_expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)