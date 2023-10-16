import logging
from core.models import User, InteractiveUser
from secrets import token_hex

logger = logging.getLogger(__name__)


class SamlUserService:
    def login(self, username: str, user_data: dict):
        user = User.objects.prefetch_related(
            'i_user').filter(username=username).first()
        if not user:
            user = self._create_user(username, user_data)
        else:
            self._update_user(user, user_data)
        self._update_user_legal_entities(user, user_data)
        
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
            password="locked" # this is password hash, it means no password will match
        )
        i_user.save()
        core_user = User(username=username)
        core_user.i_user = i_user
        core_user.save()
        return core_user

    def _update_user(self, user: User, user_data: dict) -> None:
        data_first_name = user_data.get('FirstName')[0]
        data_last_name = user_data.get('LastName')[0]

        # For now only first and last name can be updated with saml
        if user.i_user.other_names != data_first_name \
                or user.i_user.last_name != data_last_name:
            user.i_user.save_history()
            user.i_user.other_names = data_first_name
            user.i_user.last_name = data_last_name
            user.i_user.save()

    def _update_user_legal_entities(self, user: User, user_data: dict) -> None:
        # TODO Handling of legal entities
        pass
