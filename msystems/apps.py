from django.apps import AppConfig

DEFAULT_CFG = {
    'saml_config': {
        # Strict mode: SAML responses must be validated strictly.
        "strict": True,
        "debug": False,  # Set this to True for debugging purposes.
        "sp": {
            # TODO Resolve these urls from config, currently hard-coded
            "entityId": "http://127.0.0.1:8000/api/msystems/saml/metadata/",
            "assertionConsumerService": {
                "url": "http://127.0.0.1:8000/api/msystems/saml/acs/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "http://127.0.0.1:8000/api/msystems/saml/sls/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            # X509 certificate for the SP, base64 string format
            "x509cert": "",
            # Needed to sign our messages
            "privateKey": "",
        },
        "idp": {
            "entityId": "https://mpass.staging.egov.md",
            "singleSignOnService": {
                "url": "https://mpass.staging.egov.md/login/saml/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "https://mpass.staging.egov.md/logout/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            # Mpass staging public X509 certificate, https://mpass.staging.egov.md/meta/saml
            "x509cert": "MIIDCDCCAfSgAwIBAgIQZQkLso6pM7VIIMdXosWYTTAJBgUrDgMCHQUAMBsxGTAXBgNVBAMTEHRlc3RtcGFzcy5nb3YubWQwHhcNMTQwNzE2MTEwOTU1WhcNMzkxMjMxMjM1OTU5WjAbMRkwFwYDVQQDExB0ZXN0bXBhc3MuZ292Lm1kMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA03X1rhepQAg4ZP7LzpdiN3eBsl/wxO427bj2IkFuDdkqBxfGOlB2HYC0QYsA57UgywAsj33t1VOogzsOD3eia3Zg/lIs47x1Aw4ykVt2QA4wuZxW0GRpDoJPmDsDR0Hy9ixURNCVHCBvA6fOF7XML+PDMf6k7cGEuN/tqO1ENQM736P2w7FcDg1Kftx/5ZjSRudgkARfB4EOWzg9mvooLmEPjdm61Y1mesgqNvbQtJ7dMDl/nAMzU7sAwqfYR0WWsW/vYjXOBbIwwFU7Zh+wzdu2ZQgtWE2pU8UNAF0kpQ7e+nM3IZoZDfuAo9YwU/av8IGhkHGq+AhRr4ymO7KteQIDAQABo1AwTjBMBgNVHQEERTBDgBBVWSCwlA+0kK8Dsm8WWpbhoR0wGzEZMBcGA1UEAxMQdGVzdG1wYXNzLmdvdi5tZIIQZQkLso6pM7VIIMdXosWYTTAJBgUrDgMCHQUAA4IBAQAsVo5jlDWCof7noG518MMnT55ytA8tPTRIuedF0oTGcoA63jHCKmj5Bf58FPwlc2EjX3B0R4LxCdTKwLJrU+jrxRpcxboAJXL1g1fp5FCy5Bvt0JHb6wEqNl2Rfk1gYawJqWZCIphl6oWpXIrKk2vkeIaKrsqHb/jHILYete+mQZ+JAIZqbiM8Fusdrzp8rZ+15s9QulZ6uj4g3Zk7W8Gi9i5e2XQ5pr9UEw5SSQy6O0doxiJvSUfM6htrrQTtK2CzUCNpWz990v5ogzTaiZMbm7+zOrOAYybLL+YJBA9ENb3M3rQY5CTtTRF/7KO61CIkEIr+kln3GocUw5hfl9z5",
        },

        # Advanced security options, comment out for default
        "security": {
            # "nameIdEncrypted": false,
            # "authnRequestsSigned": false,
            # "logoutRequestSigned": false,
            # "logoutResponseSigned": false,
            # "signMetadata": True,
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

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CFG)
        self._load_config(cfg)

    @classmethod
    def _load_config(cls, cfg):
        for field in cfg:
            if hasattr(MsystemsConfig, field):
                setattr(MsystemsConfig, field, cfg[field])
