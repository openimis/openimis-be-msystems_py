from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from msystems.views import mpass, mpay

saml_urls = [
    path("login/", mpass.login),
    path("logout/", mpass.logout),
    path("metadata/", mpass.metadata),
    path("acs/", mpass.acs),
]

urlpatterns = [
    path("saml/", include(saml_urls)),
    path("mpay/", csrf_exempt(mpay.mpay_app)),
    path("mpay_payment/", mpay.mpay_bill_payment_redirect),
]
