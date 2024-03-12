import graphene

from django.utils.translation import gettext as _
from django.contrib.auth.models import AnonymousUser

from insuree.apps import InsureeConfig
from msystems.client.mconnect import MconnectClient
from msystems.gql_queries import *


class Query(graphene.ObjectType):
    fetch_worker_data = graphene.Field(
        FetchWorkerDataGQLType,
        idpn=graphene.ID(required=True),
    )

    def resolve_fetch_worker_data(self, info, idpn=None, **kwargs):
        Query._check_permissions(info.context.user, InsureeConfig.gql_query_insuree_perms)
        client = MconnectClient()

        result = client.get_person(idpn)

        if not result['success']:
            raise ValueError("msystems.mconnect.get_person_failed")

        return FetchWorkerDataGQLType(**result['data'])

    @staticmethod
    def _check_permissions(user, perms):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(perms):
            raise PermissionError(_("Unauthorized"))
