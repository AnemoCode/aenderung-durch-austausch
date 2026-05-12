from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.accounts.admin import UserAdmin

User = get_user_model()


class UserAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)
        self.factory = RequestFactory()

    def test_superuser_can_see_groups_and_permissions(self):
        superuser = User(email='su@example.com', name='SU', is_superuser=True, is_staff=True)
        request = self.factory.get('/')
        request.user = superuser
        readonly = self.admin.get_readonly_fields(request)
        self.assertNotIn('groups', readonly)
        self.assertNotIn('user_permissions', readonly)

    def test_staff_non_superuser_cannot_edit_groups_and_permissions(self):
        staff = User(email='staff@example.com', name='Staff', is_superuser=False, is_staff=True)
        request = self.factory.get('/')
        request.user = staff
        readonly = self.admin.get_readonly_fields(request)
        self.assertIn('groups', readonly)
        self.assertIn('user_permissions', readonly)

    def test_list_display_includes_email(self):
        self.assertIn('email', self.admin.list_display)

    def test_list_display_includes_name(self):
        self.assertIn('name', self.admin.list_display)
