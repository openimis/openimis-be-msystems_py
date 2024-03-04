import datetime as py_datetime
from zeep.wsse.signature import _make_sign_key, _sign_envelope_with_key, _make_verify_key, _verify_envelope_with_key
from lxml import etree

from core import datetime

ns_envelope = "http://schemas.xmlsoap.org/soap/envelope/"
ns_wss_util = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
ns_wss_s = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"

created_xpath = f"./{{{ns_envelope}}}Header/{{{ns_wss_s}}}Security/{{{ns_wss_util}}}Timestamp/{{{ns_wss_util}}}Created"
expires_xpath = f"./{{{ns_envelope}}}Header/{{{ns_wss_s}}}Security/{{{ns_wss_util}}}Timestamp/{{{ns_wss_util}}}Expires"


def add_signature(root, key, cert):
    key = _make_sign_key(key, cert, None)
    return _sign_envelope_with_key(root, key, None, None)


def verify_signature(root, cert):
    key = _make_verify_key(cert)
    return _verify_envelope_with_key(root, key)


def add_timestamp(root):
    dt_now = datetime.datetime.from_ad_datetime(py_datetime.datetime.now(tz=py_datetime.timezone.utc))
    dt_expires = dt_now + datetime.datetimedelta(minutes=5)

    header = etree.SubElement(root, etree.QName(ns_envelope, "Header"))
    security = etree.SubElement(header, etree.QName(ns_wss_s, "Security"))
    timestamp = etree.SubElement(security, etree.QName(ns_wss_util, "Timestamp"))
    created = etree.SubElement(timestamp, etree.QName(ns_wss_util, "Created"))
    created.text = dt_now.isoformat()
    expires = etree.SubElement(timestamp, etree.QName(ns_wss_util, "Expires"))
    expires.text = dt_expires.isoformat()


def verify_timestamp(root):
    dt_now = datetime.datetime.from_ad_datetime(py_datetime.datetime.now(tz=py_datetime.timezone.utc))
    created, expires = root.find(created_xpath), root.find(expires_xpath)

    if created is None:
        raise ValueError('Created timestamp not found')
    dt_created = datetime.datetime.fromisoformat(created.text)

    if expires is None:
        raise ValueError('Expires timestamp not found')
    dt_expires = datetime.datetime.fromisoformat(expires.text)

    if dt_created > dt_now:
        raise ValueError('Created timestamp is in the future')
    if dt_expires < dt_now:
        raise ValueError('Envelope has expired')
