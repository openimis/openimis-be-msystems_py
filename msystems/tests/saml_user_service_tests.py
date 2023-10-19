from django.test import TestCase
from copy import deepcopy
from location.models import Location

from msystems.services import SamlUserService
from msystems.tests.data import example_username, example_user_data
from core.models import User, InteractiveUser


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

        self.assertTrue(User.objects.filter(
            username=example_username).exists())
        self.assertTrue(InteractiveUser.objects.filter(
            login_name=example_username, validity_to__isnull=True).exists())

    def test_multiple_logina_data_updated(self):
        self.service.login(username=example_username,
                           user_data=example_user_data)

        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, last_name=example_user_data['LastName'][0], validity_to__isnull=True)
                        .exists())

        example_user_data_updated = deepcopy(example_user_data)
        example_user_data_updated['LastName'][0] = "Test_Last_Name_Updated"

        self.service.login(username=example_username,
                           user_data=example_user_data_updated)

        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, last_name=example_user_data['LastName'][0], validity_to__isnull=False)
                        .exists())
        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, last_name=example_user_data_updated['LastName'][0], validity_to__isnull=True)
                        .exists())

    def test_multiple_logins_no_data_update(self):
        self.service.login(username=example_username,
                           user_data=example_user_data)

        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, last_name=example_user_data['LastName'][0], validity_to__isnull=True)
                        .exists())

        self.service.login(username=example_username,
                           user_data=example_user_data)

        self.assertFalse(InteractiveUser.objects
                         .filter(login_name=example_username, validity_to__isnull=False)
                         .exists())
        self.assertTrue(InteractiveUser.objects
                        .filter(login_name=example_username, validity_to__isnull=True)
                        .exists())
        
    def test_user_district(self):
        self.service.login(username=example_username,
                           user_data=example_user_data)
        
        i_user = InteractiveUser.objects.get(login_name=example_username)
        district = Location.objects.get(code='MD01')
        self.assertEqual([ud.location for ud in i_user.userdistrict_set.all()], [district])
        