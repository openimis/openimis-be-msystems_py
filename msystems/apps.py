from django.apps import AppConfig

DEFAULT_CFG = {
    # URL to be redirected to after successful login
    'mpass_login_redirect': "",
    # Mpass configurations
    'mpass_config': {
        # Strict mode: SAML responses must be validated strictly.
        "strict": True,
        # Set this to True for debugging purposes.
        "debug": False,
        # Service provider settings
        "sp": {
            # entityId, acs and sls urls are validated by IdP
            "entityId": "",
            # callback url for login attempts
            "assertionConsumerService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            # endpoint called from idp after logout
            "singleLogoutService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            # X509 certificate for the SP, PEM string format
            "x509cert": "",
            # RSA private key, PEM string format
            "privateKey": ""
        },
        "idp": {
            "entityId": "",
            # login endpoint to redirect to from openIMIS
            "singleSignOnService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            # endpoint to call after logout from openIMIS
            "singleLogoutService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            # Idp public X509 certificate
            "x509cert": ""
        },
        # Advanced security options
        "security": {
            "authnRequestsSigned": True,
            "logoutRequestSigned": True,
            "logoutResponseSigned": True,
            "signMetadata": True,
        },
    },
    # Mpay configurations
    'mpay_config': {
        'service_id': "SERVICE1",
        # The same as mpass cert
        'service_certificate': "",
        # The same as mpass private key
        'service_private_key': "",
        # Mpay certificate, PEM string format
        'mpay_cert': "",
        # Default account info for voucher payments
        'mpay_destination_account': {
            'BankCode': "",
            'BankFiscalCode': "",
            'BankAccount': "",
            'BeneficiaryName': ""
        }
    }
}


class MsystemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msystems'

    ##### DO NOT  CHANGE THIS ####
    ADMIN = 'Admin'
    INSPECTOR = 'Inspector'
    EMPLOYER = 'Employer'
    IMIS_ADMIN = 'IMIS Administrator'
    ENROLMENT_OFFICER = 'Enrolment Officer'
    ##### ------------------ ####

    mpass_config = None
    mpass_login_redirect = None

    mpay_config = None

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CFG)
        self._load_config(cfg)

    @classmethod
    def _load_config(cls, cfg):
        for field in cfg:
            if hasattr(MsystemsConfig, field):
                setattr(MsystemsConfig, field, cfg[field])
