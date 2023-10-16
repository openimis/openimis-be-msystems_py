from django.apps import AppConfig

DEFAULT_CFG = {
    # URL to be redirected to after successful login
    'base_login_redirect': "",
    'saml_config': {
        # Strict mode: SAML responses must be validated strictly.
        "strict": True,
        # Set this to True for debugging purposes.
        "debug": False,
        # Service provider settinhs
        "sp": {
            # entityId, acs and sls urls are validated by IdP
            "entityId": "",
            # callback url for login attemps
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
            # -----BEGIN CERTIFICATE-----
            # some base 64 string
            # -----END CERTIFICATE-----
            "x509cert": "",
            # RSA private key, PEM string format
            # -----BEGIN PRIVATE KEY-----
            # some base 64 string
            # -----END PRIVATE KEY-----
            "privateKey": ""
        },
        "idp": {
            "entityId": "",
            # login endpoint to redirect to
            "singleSignOnService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            # endpoint to call after logout from openimis
            "singleLogoutService": {
                "url": "",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            # Idp public X509 certificate
            "x509cert": ""
        },

        # Advanced security options, comment out for default
        "security": {
            # "nameIdEncrypted": false,
            "authnRequestsSigned": True,
            "logoutRequestSigned": True,
            "logoutResponseSigned": True,
            "signMetadata": True,
            # "wantMessagesSigned": false,
            # "wantAssertionsSigned": false,
            # "wantNameId": true,
            # "wantNameIdEncrypted": false,
            # "wantAssertionsEncrypted": false,
            # "allowSingleLabelDomains": false,
            # "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            # "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
            # "rejectDeprecatedAlgorithm": true
        },

        # TODO
        # Additional info for metadata
        # "contactPerson": {
        #     "technical": {
        #         "givenName": "technical_name",
        #         "emailAddress": "technical@example.com"
        #     },
        #     "support": {
        #         "givenName": "support_name",
        #         "emailAddress": "support@example.com"
        #     }
        # },
        # "organization": {
        #     "en-US": {
        #         "name": "sp_test",
        #         "displayname": "SP test",
        #         "url": "http://sp.example.com"
        #     }
        # }
    }
}


class MsystemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msystems'

    saml_config = None
    base_login_redirect = None

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CFG)
        self._load_config(cfg)

    @classmethod
    def _load_config(cls, cfg):
        for field in cfg:
            if hasattr(MsystemsConfig, field):
                setattr(MsystemsConfig, field, cfg[field])
