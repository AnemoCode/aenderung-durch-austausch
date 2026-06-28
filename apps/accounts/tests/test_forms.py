from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.forms import EmailLoginForm, RegistrationForm

User = get_user_model()


class EmailLoginFormTests(TestCase):
    def test_email_field_present(self):
        form = EmailLoginForm()
        self.assertIn('username', form.fields)
        self.assertEqual(form.fields['username'].label, 'E-Mail-Adresse')


class RegistrationFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        data.update(overrides)
        return data

    def test_valid_form_is_valid(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_mismatching_passwords_invalid(self):
        form = RegistrationForm(data=self._valid_data(password2='WrongPass123!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_weak_password_rejected_by_validators(self):
        form = RegistrationForm(data=self._valid_data(password1='password', password2='password'))
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_missing_name_invalid(self):
        form = RegistrationForm(data=self._valid_data(name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_missing_email_invalid(self):
        form = RegistrationForm(data=self._valid_data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_save_creates_user_with_hashed_password(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_save_commit_false_does_not_persist(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertIsNone(user.pk)
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_duplicate_email_invalid(self):
        User.objects.create_user(email='test@example.com', name='Existing', password='pw123456!')
        form = RegistrationForm(data=self._valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
