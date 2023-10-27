import logging

from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from msystems.apps import MsystemsConfig
from msystems.services import SamlUserService
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings
from graphql_jwt.decorators import jwt_cookie
from graphql_jwt.shortcuts import get_token, create_refresh_token

logger = logging.getLogger(__name__)


def _build_auth(request, slo_workaround=False) -> OneLogin_Saml2_Auth:
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
    if slo_workaround:
        #  https://github.com/SAML-Toolkits/python3-saml/issues/205
        if "SAMLResponse" in req["post_data"]:
            req['get_data']['SAMLResponse'] = req["post_data"].get("SAMLResponse")
        if "SAMLRequest" in req["post_data"]:
            req['get_data']['SAMLRequest'] = req["post_data"].get("SAMLRequest")
    return OneLogin_Saml2_Auth(req, MsystemsConfig.saml_config)


@require_GET
def login(request):
    # From python3-saml django example
    auth = _build_auth(request)
    login_request = auth.login(return_to=MsystemsConfig.base_login_redirect)
    return redirect(login_request)


@require_GET
@jwt_cookie
def logout(request):
    auth = _build_auth(request)
    request.delete_jwt_cookie = True
    request.delete_refresh_token_cookie = True
    logout_request = auth.logout(name_id=request.user.username)
    return redirect(logout_request)


@require_GET
def metadata(request):
    # from python3-saml docs
    saml_settings = OneLogin_Saml2_Settings(
        settings=MsystemsConfig.saml_config, sp_validation_only=True)
    saml_metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(saml_metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=saml_metadata, content_type='text/xml')
    else:
        errors_str = ', '.join(errors)
        logger.error(
            "Errors while generating saml metadata view: %s", errors_str)
        resp = HttpResponseServerError(content=errors_str)
    return resp


def _handle_acs_login(request):
    auth = _build_auth(request)
    auth.process_response()
    errors = auth.get_errors()

    if errors:
        logger.error("SAML Login failed: %s\n%s", str(errors[-1]), auth.get_last_error_reason())
        # TODO Add information about failed login attempt for the user
        return redirect(MsystemsConfig.base_login_redirect)

    username = auth.get_nameid()
    user_data = auth.get_attributes()

    user = SamlUserService().login(username=username, user_data=user_data)

    # Tokens to be set in cookies
    request.jwt_token = get_token(user)
    request.jwt_refresh_token = create_refresh_token(user)

    if 'RelayState' in request.POST and _validate_relay_state(request.POST['RelayState']):
        return redirect(auth.redirect_to(request.POST['RelayState']))
    else:
        return redirect(MsystemsConfig.base_login_redirect)


def _handle_acs_logout(request):
    auth = _build_auth(request, slo_workaround=True)
    # We do not use local session, we are telling the lib not to touch it
    auth.process_slo(keep_local_session=True)
    errors = auth.get_errors()

    if not errors:
        request.delete_jwt_cookie = True
        request.delete_refresh_token_cookie = True

        if 'RelayState' in request.POST and _validate_relay_state(request.POST['RelayState']):
            return redirect(auth.redirect_to(request.POST['RelayState']))
        else:
            return redirect(MsystemsConfig.base_login_redirect)
    else:
        logger.error("SAML Logout failed: %s\n%s", str(
            errors[-1]), auth.get_last_error_reason())
        # TODO Add information about failed login attempt for the user
        return redirect(MsystemsConfig.base_login_redirect)


# Saml have its own csrf protection, django not needed
@csrf_exempt
# This is required as mpass calls this enpoint from iframe
@xframe_options_exempt
@jwt_cookie
@require_POST
def acs(request):
    if 'SAMLResponse' in request.POST:
        # Probably login response
        return _handle_acs_login(request)
    elif 'SAMLRequest' in request.POST:
        # Probably logout request
        return _handle_acs_logout(request)
    else:
        return HttpResponseBadRequest("Missing SAML payload")


def _validate_relay_state(relay_state):
    # To avoid 'Open Redirect' attacks, before execute the redirection confirm
    # the value of the 'RelayState' is a trusted URL.
    # Currently, the only valid RelayState base_login_redirect
    return relay_state == MsystemsConfig.base_login_redirect
