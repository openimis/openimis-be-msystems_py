from zeep import Plugin
from zeep.exceptions import SignatureVerificationFailed

from msystems.xml_utils import add_timestamp, add_signature, verify_timestamp, verify_signature


class SoapClientError(Exception):
    pass


class SoapWssePlugin(Plugin):
    def __init__(self, service_private_key, service_certificate, mconnect_certificate):
        self.service_certificate = service_certificate
        self.service_private_key = service_private_key
        self.client_certificate = mconnect_certificate

    def egress(self, envelope, http_headers, operation, binding_options):
        root = envelope

        add_timestamp(root)
        add_signature(root, self.service_private_key, self.service_certificate)

        return envelope, http_headers

    def ingress(self, envelope, http_headers, operation):
        try:
            verify_timestamp(envelope)
        except ValueError as e:
            raise SoapClientError(str(e))

        try:
            verify_signature(envelope, self.client_certificate)
        except SignatureVerificationFailed:
            raise SoapClientError("Envelope signature verification failed")

        return envelope, http_headers
