from zeep import Client, Plugin, Settings
from zeep.exceptions import SignatureVerificationFailed

from msystems.apps import MsystemsConfig
from msystems.xml_utils import add_signature, verify_signature, add_timestamp, verify_timestamp


class MconnectClientError(Exception):
    pass


class SoapWssePlugin(Plugin):
    def __init__(self, service_private_key, service_certificate, mconnect_certificate):
        self.service_certificate = service_certificate
        self.service_private_key = service_private_key
        self.mconnect_certificate = mconnect_certificate

    def egress(self, envelope, http_headers, operation, binding_options):
        root = envelope

        add_timestamp(root)
        add_signature(root, self.service_private_key, self.service_certificate)

        return envelope, http_headers

    def ingress(self, envelope, http_headers, operation):
        try:
            verify_timestamp(envelope)
        except ValueError as e:
            raise MconnectClientError(str(e))

        try:
            verify_signature(envelope, self.mconnect_certificate)
        except SignatureVerificationFailed:
            raise MconnectClientError("Envelope signature verification failed")

        return envelope, http_headers


class MconnectClient:
    def __init__(self):
        self.url = MsystemsConfig.mconnect_config['url']

        # Service handler replaced with hardcoded response
        # settings = Settings(strict=False, raw_response=True)
        # self.client = Client(self.url, settings,
        #                      plugins=[SoapWssePlugin(MsystemsConfig.mconnect_config['service_private_key'],
        #                                              MsystemsConfig.mconnect_config['service_certificate'],
        #                                              MsystemsConfig.mconnect_config['mconnect_certificate'])])

    def get_person(self, idpn):
        # Service handler replaced with hardcoded response
        # service_handle = self.client.service.get('GetPerson')
        # if not service_handle:
        #     raise MconnectClientError("Service GetPerson not found")
        # response = service_handle(IDPN=idpn)
        return {"success": True, "data": {"idpn": idpn, "first_name": "John", "last_name": "Doe"}}
