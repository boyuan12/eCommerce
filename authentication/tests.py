from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Profile

# Create your tests here.
class AuthenticationTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="example@example.com", password="example").save()
        user = User.objects.get(username="example@example.com")
        Profile(user_id=user.id, role=0, address="", city="", state="", country="", zip="").save()
        self.client = Client()

    def register(self):
        rv = self.client.post("/auth/register/", {
            "first-name": "",
            "last-name": "",
            "email": "hello",
            "country-code": "",
            "phone-number": "",
            "password": "world",
            "role": 0,
            "address": "",
            "address2": "",
            "city": "",
            "state": "",
            "country": "",
            "zip": ""
        })
        return rv


    def login(self, email, password):
        print(User.objects.all())
        rv = self.client.post("/auth/login/", {
            "email": email,
            "password": password
        })
        return rv


    # def test_register(self):
    #     rv = self.register()
    #     print(rv.content)
    #     assert rv.status_code == 200


    def test_login(self):
        rv = self.login("example", "example")
        assert b'You entered wrong credentials.' in rv.content

        rv = self.login("example@example.com", "example")
        assert b'Please complete initial 2FA first.' in rv.content
