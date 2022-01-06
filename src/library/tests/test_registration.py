from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from library.models import *

class RegistrationTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345', first_name="Jane", last_name="Doe", email="mail@dummy.com",)
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_form_content(self):
        response = self.client.get((reverse('library:register')))
        self.assertContains(response, 'username')
        self.assertContains(response, 'First name')
        self.assertContains(response, 'Last name')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Password')

    def test_correct_input(self):
        form_data = {'username': "dummy",
                     'email': "dummy@dummy.com",
                     "first_name": "Toni",
                     "last_name": "Tester",
                     "password1": "Test1234",
                     "password2": "Test1234"}
        response = self.client.post(reverse('library:index'), form_data)
        self.assertEqual(response.status_code, 200)

        #users = get_user_model().objects.all()
        #self.assertEqual(users.count(), 1)

    def username_missing(self):
        form_data = {'email': "dummy@dummy.com",
                     "first_name": "Toni",
                     "last_name": "Tester",
                     "password1": "Test1234",
                     "password2": "Test1234"}
        response = self.client.post(reverse('library:index'), form_data)
        self.assertEqual(response.status_code, 200)
        #Check Pop-up
        return False


    def test_username_already_exists(self):
        form_data = {'username': "testuser1",
                     'email': "dummy@dummy.com",
                     "first_name": "Toni",
                     "last_name": "Tester",
                     "password1": "Test1234",
                     "password2": "Test1234"}
        response = self.client.post(reverse('library:register'), form_data)
        self.assertContains(response,"Unsuccessful registration. Invalid information.")

    def test_email_already_exists(self):
        form_data = {'username': "testuser5",
                     'email': "mail@dummy.com",
                     "first_name": "Toni",
                     "last_name": "Tester",
                     "password1": "Test1234",
                     "password2": "Test1234"}
        response = self.client.post(reverse('library:register'), form_data)
        self.assertContains(response, "Unsuccessful registration. Invalid information.")

    # Redirect to startpage if user is logged in
    # Not working yet
    # def test_redirect_if_logged_in(self):
    #     login = self.client.login(username='testuser1', password='12345')
    #     response = self.client.get(reverse('library:index'))
    #     self.assertRedirects(response, '')
