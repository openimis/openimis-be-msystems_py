from zeep import Client, Settings

from msystems.apps import MsystemsConfig
from msystems.client.utils import SoapWssePlugin, SoapClientError


class MconnectClient:

    def __init__(self):
        self.url = MsystemsConfig.mconnect_config['url']

        settings = Settings(strict=False, raw_response=True)
        self.client = Client(wsdl=self.url,
                             settings=settings,
                             plugins=[SoapWssePlugin(MsystemsConfig.mconnect_config['service_private_key'],
                                                     MsystemsConfig.mconnect_config['service_certificate'],
                                                     MsystemsConfig.mconnect_config['mconnect_certificate'])])

    def get_person(self, idpn):
        service_handle = self.client.service['GetPerson']
        if not service_handle:
            raise SoapClientError("Service GetPerson not found")
        return service_handle(IDPN=idpn)
