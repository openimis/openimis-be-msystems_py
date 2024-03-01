from zeep.wsse.signature import _make_sign_key, _sign_envelope_with_key, _make_verify_key, _verify_envelope_with_key


def sign_envelope(envelope, key, cert):
    key = _make_sign_key(key, cert, None)
    return _sign_envelope_with_key(envelope, key, None, None)


def verify_envelope(envelope, cert):
    key = _make_verify_key(cert)
    return _verify_envelope_with_key(envelope, key)
