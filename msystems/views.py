from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from msystems.apps import MsystemsConfig
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings, OneLogin_Saml2_Utils


@require_GET
def login(request):
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
    
    # TODO Add RelayState to /front/home
    return redirect(auth.login())


@require_GET
def metadata(request):
    # req = prepare_django_request(request)
    # auth = init_saml_auth(req)
    # saml_settings = auth.get_settings()
    saml_settings = OneLogin_Saml2_Settings(
        settings=MsystemsConfig.saml_config, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp


@csrf_exempt
@require_POST
def acs(request):
    req = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy()
    }
    print(req['post_data'])
    auth = OneLogin_Saml2_Auth(req, MsystemsConfig.saml_config)
    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        print("----logged_in")
        print(auth.get_attributes())
        print(auth.get_nameid())
        print(auth.get_nameid_format())
        print(auth.get_nameid_nq())
        print(auth.get_nameid_spnq())
        print(auth.get_session_index())
        if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
            # To avoid 'Open Redirect' attacks, before execute the redirection confirm
            # the value of the req['post_data']['RelayState'] is a trusted URL.
            return redirect(auth.redirect_to(req['post_data']['RelayState']))
    else:
        print("----not logged_in")
        print(errors[-1])
        print(auth.get_last_error_reason())
    return HttpResponse("Ok")


@csrf_exempt
@require_POST
def sls(request):
    return HttpResponse("Ok")