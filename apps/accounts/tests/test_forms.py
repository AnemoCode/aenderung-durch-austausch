from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.forms import EmailLoginForm, RegistrationForm

User = get_user_model()


class EmailLoginFormTests(TestCase):
    def test_username_field_is_email_type(self):
        form = EmailLoginForm()
        self.assertIn('username', form.fields)
        from django import forms as django_forms
        self.assertIsInstance(form.fields['username'], django_forms.EmailField)

    def test_username_label(self):
        form = EmailLoginForm()
        self.assertIn('E-Mail', form.fields['username'].label)


class RegistrationFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password1': 'str0ng!Passw0rd',
            'password2': 'str0ng!Passw0rd',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch_raises_error(self):
        form = RegistrationForm(data=self._valid_data(password2='different'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_weak_password_raises_error(self):
        form = RegistrationForm(data=self._valid_data(password1='123', password2='123'))
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_save_hashes_password(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password('str0ng!Passw0rd'))

    def test_save_commit_false(self):
        form = RegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertIsNone(user.pk)

    def test_duplicate_email_raises_error(self):
        User.objects.create_user(email='testuser@example.com', name='Existing', password='pw')
        form = RegistrationForm(data=self._valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_empty_name_raises_error(self):
        form = RegistrationForm(data=self._valid_data(name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
