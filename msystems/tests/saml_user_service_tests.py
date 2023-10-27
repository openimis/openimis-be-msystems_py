from django.test import TestCase
from copy import deepcopy
from location.models import Location
from msystems.apps import MsystemsConfig

from msystems.services import SamlUserService
from msystems.tests.data import example_username, example_user_data, example_user_data_multiple_ph
from core.models import User, InteractiveUser, UserRole, Role
from policyholder.models import PolicyHolder


class SamlUserServiceTestCase(TestCase):
    service = None

    @classmethod
    def setUpClass(cls):
        super(SamlUserServiceTestCase, cls).setUpClass()
        cls.service = SamlUserService()

    def test_login(self):
        self.assertFalse(User.objects.filter(
            username=example_username).exists())
        self.assertFalse(InteractiveUser.objects.filter(
            login_name=example_username, validity_to__isnull=True).exists())

        self.service.login(username=example_username,
                           user_data=example_user_data)

        user_instance = InteractiveUser.objects.filter(
            login_name=example_username, validity_to__isnull=True)

        self.assertTrue(User.objects.filter(
            username=example_username).exists())
        self.assertTrue(user_instance.exists())
        self.assertEquals(UserRole.objects
                          .filter(user=user_instance).role, Role.objects.filter(is_system=MsystemsConfig.INSPECTOR_ID))

    def test_multiple_logina_data_updated(self):
        self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, last_name=example_user_data['LastName'][0],
                                validity_to__isnull=True)
                        .exists())

        example_user_data_updated = deepcopy(example_user_data)
        example_user_data_updated['LastName'][0] = "Test_Last_Name_Updated"
        example_user_data_updated['Role'] = ["Inspector"]

        self.service.login(username=example_username, user_data=example_user_data_updated)
        active_user = InteractiveUser.objects.filter(login_name=example_username,
                                                     last_name=example_user_data_updated['LastName'][0],
                                                     validity_to__isnull=True)
        active_role_qs = UserRole.objects.filter(user=active_user, validity_to__isnull=True)
        deleted_role_qs = UserRole.objects.filter(user=active_user, validity_to__isnull=False)

        self.assertTrue(
            InteractiveUser.objects.filter(login_name=example_username, last_name=example_user_data['LastName'][0],
                                           validity_to__isnull=False).exists())
        self.assertTrue(active_user.exists())
        self.assertEquals(active_role_qs.count(), 1)
        self.assertEquals(deleted_role_qs.count(), 1)
        self.assertEquals(active_role_qs.role, Role.objects.filter(is_system=MsystemsConfig.INSPECTOR_ID))

    def test_multiple_logins_no_data_update(self):
        self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(
            InteractiveUser.objects.filter(login_name=example_username, last_name=example_user_data['LastName'][0],
                                           validity_to__isnull=True).exists())

        self.service.login(username=example_username, user_data=example_user_data)

        active_user = InteractiveUser.objects.filter(login_name=example_username, validity_to__isnull=True)
        user_role_qs = UserRole.objects.filter(user=active_user, validity_to__isnull=True)

        self.assertFalse(InteractiveUser.objects
                         .filter(login_name=example_username, validity_to__isnull=False)
                         .exists())
        self.assertTrue(active_user.exists())
        self.assertEquals(user_role_qs.count(), 1)
        self.assertEquals(user_role_qs.role, Role.objects.filter(is_system=MsystemsConfig.INSPECTOR_ID))

    def test_user_district(self):
        self.service.login(username=example_username, user_data=example_user_data)

        i_user = InteractiveUser.objects.get(login_name=example_username)
        district = Location.objects.get(code='MD01')
        self.assertEqual([ud.location for ud in i_user.userdistrict_set.all()], [district])

    def test_create_policyholder(self):
        user = self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                                    policyholderuser__is_deleted=False).exists())

    def test_update_policyholder(self):
        user = self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=False).exists())

        example_user_data_updated = deepcopy(example_user_data)
        example_user_data_updated['OrganizationAdministrator'][0] = "Test New Organisation 1 2345234523999"

        user = self.service.login(username=example_username, user_data=example_user_data_updated)

        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=True).exists())
        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523999', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=False).exists())
        self.assertEqual(2, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user).count())

    def test_update_policyholder_name(self):
        user = self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=False).exists())

        example_user_data_updated = deepcopy(example_user_data)
        example_user_data_updated['OrganizationAdministrator'][0] = "Test New Name Organisation 1 2345234523452"

        user = self.service.login(username=example_username, user_data=example_user_data_updated)

        self.assertTrue(PolicyHolder.objects.filter(code='2345234523452', trade_name='Test New Name Organisation 1',
                                                    is_deleted=False, policyholderuser__user=user,
                                                    policyholderuser__is_deleted=False).exists())
        self.assertEqual(1, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user).count())

    def test_revoke_policyholder(self):
        user = self.service.login(username=example_username, user_data=example_user_data_multiple_ph)

        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=False).exists())
        self.assertEqual(2, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user).count())

        example_user_data_updated = deepcopy(example_user_data_multiple_ph)
        example_user_data_updated['OrganizationAdministrator'].pop()

        user = self.service.login(username=example_username, user_data=example_user_data_updated)

        self.assertEqual(1, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user,
                                                        policyholderuser__is_deleted=False).count())
        self.assertEqual(1, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user,
                                                        policyholderuser__is_deleted=True).count())

    def test_add_policyholder(self):
        user = self.service.login(username=example_username, user_data=example_user_data)

        self.assertTrue(
            PolicyHolder.objects.filter(code='2345234523452', is_deleted=False, policyholderuser__user=user,
                                        policyholderuser__is_deleted=False).exists())
        self.assertEqual(1, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user).count())

        example_user_data_updated = deepcopy(example_user_data)
        example_user_data_updated['OrganizationAdministrator'].append("Test New Organisation 2345234523999")

        user = self.service.login(username=example_username, user_data=example_user_data_updated)

        self.assertEqual(2, PolicyHolder.objects.filter(is_deleted=False, policyholderuser__user=user,
                                                        policyholderuser__is_deleted=False).count())
