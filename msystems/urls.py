from django.urls import path, include
from msystems import views


saml_urls = [
    path("login/", views.login),
    path("metadata/", views.metadata),
    path("acs/", views.acs),
    path("sls/", views.sls),
]

urlpatterns = [
    path("saml/", include(saml_urls)),
]
