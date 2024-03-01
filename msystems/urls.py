from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from msystems.apps import MsystemsConfig
from msystems.views import mpass, mpay

saml_urls = [
    path("login/", mpass.login),
    path("logout/", mpass.logout),
    path("metadata/", mpass.metadata),
    path("acs/", mpass.acs),
]

urlpatterns = []

if MsystemsConfig.enable_mpass:
    urlpatterns += [path("saml/", include(saml_urls))]

if MsystemsConfig.enable_mpay:
    urlpatterns += [path("mpay/", csrf_exempt(mpay.mpay_app))]
