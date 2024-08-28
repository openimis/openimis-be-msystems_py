import logging

from zeep import Client, Settings

from core.models import User
from msystems.apps import MsystemsConfig
from msystems.client.utils import SoapWssePlugin, SoapClientError
from policyholder.models import PolicyHolder

logger = logging.getLogger(__name__)


class MConnectClient:

    def __init__(self):
        self.url = MsystemsConfig.mconnect_config['url']

        settings = Settings(strict=False, raw_response=False)
        self.client = Client(wsdl=self.url,
                             settings=settings,
                             plugins=[SoapWssePlugin(MsystemsConfig.mconnect_config['service_private_key'],
                                                     MsystemsConfig.mconnect_config['service_certificate'],
                                                     MsystemsConfig.mconnect_config['mconnect_certificate'])])

    def get_person(self, idnp: str, user: User = None, economic_unit: PolicyHolder = None):
        service_handle = self.client.service['GetPerson']
        if not service_handle:
            raise SoapClientError("Service GetPerson not found")

        # Bounds for headers and idnp from Mconnect documentation, should not be exceeded in normal operation
        # Added for extra protection

        username = user.username[:13] if user else MsystemsConfig.mconnect_config['get_person_calling_user'][:13]
        eu_code = economic_unit.code[:13] if economic_unit \
            else MsystemsConfig.mconnect_config['get_person_calling_entity'][:13]

        headers = {
            "CallingUser":username,
            "CallingEntity":eu_code,
            "CallBasis": MsystemsConfig.mconnect_config['get_person_call_basis'][:256],
            "CallReason": MsystemsConfig.mconnect_config['get_person_call_reason'][:512]
        }

        try:
            return service_handle(IDNP=idnp[:13], _soapheaders=headers)
        except Exception as e:
            logger.error("Error during Mconnect request", exc_info=e)
            raise SoapClientError(str(e))
