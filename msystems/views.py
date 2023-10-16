import logging

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from msystems.apps import MsystemsConfig
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings, OneLogin_Saml2_Utils

logger = logging.getLogger(__name__)


@require_GET
def login(request):
    # From python3-saml django example
    req = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy()
    }
    auth = OneLogin_Saml2_Auth(req, MsystemsConfig.saml_config)

    # add a redirect to base_login_redirect from a successful login attempt
    login_request = auth.login(return_to=MsystemsConfig.base_login_redirect)
    return redirect(login_request)


@require_GET
def metadata(request):
    # from python3-saml docs
    saml_settings = OneLogin_Saml2_Settings(
        settings=MsystemsConfig.saml_config, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        errors_str = ', '.join(errors)
        logger.error(
            "Errors while generating saml metadata view: %s", errors_str)
        resp = HttpResponseServerError(content=errors_str)
    return resp


# Saml have it's own csrf protection, django not needed
@csrf_exempt
@require_POST
def acs(request):
    # From python3-saml django example
    req = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy()
    }

    auth = OneLogin_Saml2_Auth(req, MsystemsConfig.saml_config)
    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        user = auth.get_nameid
        user_data = auth.get_attributes()

        # TODO remove the log and add proper user handling
        logger.debug("User %s logged in with data %s", user, str(user_data))

        if 'RelayState' in req['post_data'] and _validate_relay_state(req['post_data']['RelayState']):
            return redirect(auth.redirect_to(req['post_data']['RelayState']))
    else:
        logger.error("Login attempt failed: %s\n%s", str(
            errors[-1]), auth.get_last_error_reason())
        # TODO Add information about failed login attempt for the user
        return redirect(MsystemsConfig.base_login_redirect)


# Saml have it's own csrf protection, django not needed
@csrf_exempt
@require_POST
def sls(request):
    # TODO implement SLS
    return HttpResponse("Ok")


def _validate_relay_state(relay_state):
    # To avoid 'Open Redirect' attacks, before execute the redirection confirm
    # the value of the 'RelayState' is a trusted URL.
    # Currenly the only valid RelayState base_login_redirect
    return relay_state == MsystemsConfig.base_login_redirect
