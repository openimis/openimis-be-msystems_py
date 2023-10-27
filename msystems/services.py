import logging
from typing import List

from core import datetime

from django.db import transaction
from django.db.models import Q
from secrets import token_hex

from core.models import User, InteractiveUser, Role, UserRole
from core.services.userServices import create_or_update_user_districts
from location.models import Location
from msystems.apps import MsystemsConfig
from policyholder.models import PolicyHolder, PolicyHolderUser

logger = logging.getLogger(__name__)


class SamlUserService:
    location = None

    def __init__(self):
        if not self.location:
            self.location = Location.objects \
                .prefetch_related('parent', 'parent__parent', 'parent__parent__parent') \
                .get(code='MV01', validity_to__isnull=True)

    def login(self, username: str, user_data: dict):
        with transaction.atomic():
            try:
                user = self._get_or_create_user(username, user_data)
                self._update_user_legal_entities(user, user_data)
                return user
            except BaseException as e:
                # Extra logging for the development, should be removed for any real data usage
                # as it will put personal information in logs
                logger.debug("Successful SAML login handling failed, username=%s, user_data=%s", username,
                             str(user_data), exc_info=e)
                raise

    def _get_or_create_user(self, username: str, user_data: dict):
        user = User.objects.prefetch_related('i_user').filter(username=username).first()
        if not user:
            user = self._create_user(username, user_data)
        else:
            self._update_user(user, user_data)
        return user

    def _create_user(self, username: str, user_data: dict) -> User:
        i_user = InteractiveUser(
            login_name=username,
            other_names=user_data.get('FirstName')[0],
            last_name=user_data.get('LastName')[0],
            language_id='en',
            audit_user_id=0,
            is_associated=False,
            private_key=token_hex(128),
            password="locked"  # this is password hash, it means no password will match
        )
        i_user.save()

        create_or_update_user_districts(i_user, [self.location.parent.parent.id], 0)

        msystem_roles = user_data.get('Role')
        if msystem_roles:
            imis_role_ids = [self._parse_msystem_role_to_imis_role_id(msystem_role_id) for msystem_role_id in
                             msystem_roles]
            self._connect_role_with_user(i_user, imis_role_ids)

        core_user = User(username=username)
        core_user.i_user = i_user
        core_user.save()
        return core_user

    def _update_user(self, user: User, user_data: dict) -> None:
        data_first_name = user_data.get('FirstName')[0]
        data_last_name = user_data.get('LastName')[0]
        msystem_roles = user_data.get('Role')
        incoming_imis_role_ids = [self._parse_msystem_role_to_imis_role_id(msystem_role_id) for msystem_role_id in
                                  msystem_roles]
        current_user_roles = Role.objects.filter(userrole__user=user.i_user).values_list('is_system', flat=True)

        # Update first and last name if they are different
        if user.i_user.other_names != data_first_name or user.i_user.last_name != data_last_name:
            self._update_user_name(user.i_user, data_first_name, data_last_name)
        if current_user_roles != incoming_imis_role_ids:
            self._update_user_roles(user.i_user, incoming_imis_role_ids)

    def _update_user_legal_entities(self, user: User, user_data: dict) -> None:
        legal_entities = self._parse_legal_entities(user_data.get('OrganizationAdministrator'))
        policyholders = [self._get_or_create_policy_holder(user, line[1], line[0]) for line in legal_entities]

        self._delete_old_user_policyholders(user, policyholders)
        self._add_new_user_policyholders(user, policyholders)

    def _update_user_name(self, i_user, first_name, last_name):
        i_user.save_history()
        i_user.other_names = first_name
        i_user.last_name = last_name
        i_user.save()

    def _parse_legal_entities(self, legal_entities) -> map:
        # The format of EU is "Name Tax_Number", splitting by the last space
        return map(lambda s: s.rsplit(' ', 1), legal_entities)

    def _get_or_create_policy_holder(self, user: User, code: str, name: str) -> PolicyHolder:
        policyholder = PolicyHolder.objects.filter(code=code, is_deleted=False).first()
        if not policyholder:
            policyholder = self._create_policyholder(user, code, name)
        else:
            self._update_policyholder(user, policyholder, name)
        return policyholder

    def _create_policyholder(self, user: User, code: str, name: str) -> PolicyHolder:
        policyholder = PolicyHolder(
            code=code,
            trade_name=name,
            locations=self.location,
            date_valid_from=datetime.datetime.now()
        )
        policyholder.save(username=user.username)
        return policyholder

    def _update_policyholder(self, user: User, policyholder: PolicyHolder, name: str):
        if policyholder.trade_name != name:
            policyholder.trade_name = name
            policyholder.save(username=user.username)

    def _delete_old_user_policyholders(self, user: User, policyholders: List[PolicyHolder] ):
        for phu in PolicyHolderUser.objects.filter(~Q(policy_holder__in=policyholders), user=user, is_deleted=False):
            phu.delete(username=user.username)

    def _add_new_user_policyholders(self, user: User, policyholders: List[PolicyHolder]):
        current_policyholders = (PolicyHolder.objects.filter(policyholderuser__user=user,
                                                             policyholderuser__is_deleted=False, is_deleted=False))
        for ph in policyholders:
            if ph not in current_policyholders:
                PolicyHolderUser(user=user, policy_holder=ph).save(username=user.username)

    def _update_user_roles(self, i_user, imis_role_ids):
        self._remove_previous_user_roles(i_user)
        self._connect_role_with_user(i_user, imis_role_ids)

    def _connect_role_with_user(self, i_user, imis_role_ids):
        user_role = UserRole.objects.create(user=i_user, role__in=imis_role_ids)
        user_role.save()

    def _remove_previous_user_roles(self, i_user):
        UserRole.objects.filter(user=i_user).delete()

    def _parse_msystem_role_to_imis_role_id(self, msystem_role):
        role_mapping = {
            MsystemsConfig.ADMIN: MsystemsConfig.ADMIN_ID,
            MsystemsConfig.EMPLOYER: MsystemsConfig.EMPLOYER_ID,
            MsystemsConfig.INSPECTOR: MsystemsConfig.INSPECTOR_ID,
        }
        return role_mapping.get(msystem_role, None)
