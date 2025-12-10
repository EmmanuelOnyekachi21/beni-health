from django.test import SimpleTestCase
from django.urls import reverse, resolve
from apps.accounts.views import (
    register, login, profile_view
)

class UrlsTest(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, register)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login)

    def test_user_profile_url_resolves(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func, profile_view)
