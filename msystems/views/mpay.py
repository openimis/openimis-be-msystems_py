import decimal
import logging
import datetime as py_datetime

from lxml import etree
from django.db import transaction
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.fault import Fault
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase
from zeep.exceptions import SignatureVerificationFailed

from core import datetime
from invoice.apps import InvoiceConfig
from invoice.models import Bill
from msystems.apps import MsystemsConfig
from msystems.soap.models import OrderDetailsQuery, GetOrderDetailsResult, OrderLine, OrderDetails, \
    PaymentConfirmation, PaymentAccount, OrderStatus
from msystems.services.xml_signature import sign_envelope, verify_envelope
from worker_voucher.models import WorkerVoucher

namespace = 'https://zilieri.gov.md'
logger = logging.getLogger(__name__)

ns_envelope = "http://schemas.xmlsoap.org/soap/envelope/"
ns_wss_util = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
ns_wss_s = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"

created_xpath = f"./{{{ns_envelope}}}Header/{{{ns_wss_s}}}Security/{{{ns_wss_util}}}Timestamp/{{{ns_wss_util}}}Created"
expires_xpath = f"./{{{ns_envelope}}}Header/{{{ns_wss_s}}}Security/{{{ns_wss_util}}}Timestamp/{{{ns_wss_util}}}Expires"


def _check_service_id(service_id):
    if service_id != MsystemsConfig.mpay_config['service_id']:
        raise Fault(faultcode='UnknownService', faultstring=f'ServiceID "{service_id} is unknown')


def _get_order(order_key):
    bill = Bill.objects.filter(code__iexact=order_key).first()
    if not bill:
        raise Fault(faultcode='InvalidParameter', faultstring=f'OrderKey "{order_key}" is unknown')
    return bill


def _get_order_line(bill, line_id):
    bill_item = bill.line_items_bill.filter(code__iexact=line_id).first()
    if not bill_item:
        raise Fault(faultcode='InvalidParameter', faultstring=f'LineID "{line_id}" is unknown')
    return bill_item


def _check_amount_due(bill_item, amount_due):
    if amount_due != bill_item.amount_total:
        raise Fault(faultcode='InvalidParameter',
                    faultstring=f'Amount "{amount_due}" does not match the order line {bill_item.code}')


def _get_voucher(bill_item):
    voucher = WorkerVoucher.objects.filter(id=bill_item.line_id).first()
    if not voucher:
        raise Fault(faultcode='InvalidParameter',
                    faultstring=f'Voucher {bill_item.line_id} for order line {bill_item.code} not found')
    return voucher


def _validate_envelope(ctx):
    root = ctx.in_document

    now = datetime.datetime.from_ad_datetime(py_datetime.datetime.now(tz=py_datetime.timezone.utc))

    created = root.find(created_xpath)
    if created is None:
        raise Fault(faultcode='InvalidRequest', faultstring='Created timestamp not found')
    created_dt = datetime.datetime.fromisoformat(created.text)

    expires = root.find(expires_xpath)
    if expires is None:
        raise Fault(faultcode='InvalidRequest', faultstring='Expires timestamp not found')
    expires_dt = datetime.datetime.fromisoformat(expires.text)

    if created_dt > now:
        raise Fault(faultcode='InvalidRequest', faultstring='Created timestamp is in the future')
    if expires_dt < now:
        raise Fault(faultcode='InvalidRequest', faultstring='Envelope has expired')
    pass

    try:
        verify_envelope(root, MsystemsConfig.mpay_config['mpay_cert'])
    except SignatureVerificationFailed:
        raise Fault(faultcode='InvalidRequest', faultstring=f'Envelope signature verification failed')


def _add_envelope_header(ctx):
    root = ctx.out_document

    dt_now = datetime.datetime.now()
    dt_expires = dt_now + datetime.datetimedelta(minutes=5)

    header = etree.SubElement(root, etree.QName(ns_envelope, "Header"))
    security = etree.SubElement(header, etree.QName(ns_wss_s, "Security"))
    timestamp = etree.SubElement(security, etree.QName(ns_wss_util, "Timestamp"))
    created = etree.SubElement(timestamp, etree.QName(ns_wss_util, "Created"))
    created.text = dt_now.isoformat()
    expires = etree.SubElement(timestamp, etree.QName(ns_wss_util, "Expires"))
    expires.text = dt_expires.isoformat()

    sign_envelope(root, MsystemsConfig.mpay_config['service_private_key'],
                  MsystemsConfig.mpay_config['service_certificate'])

    ctx.out_string = [etree.tostring(ctx.out_document)]


class MpayService(ServiceBase):
    @rpc(OrderDetailsQuery.customize(min_occurs=1, max_occurs=1, nillable=False),
         _returns=GetOrderDetailsResult.customize(min_occurs=1, max_occurs=1, nillable=False))
    def GetOrderDetails(ctx, query: OrderDetailsQuery) -> GetOrderDetailsResult:
        _check_service_id(query.ServiceID)
        bill = _get_order(query.OrderKey)

        account = PaymentAccount(**MsystemsConfig.mpay_config['mpay_destination_account'])

        order_lines = [
            OrderLine(
                AmountDue=str(bill_item.amount_total),
                LineID=bill_item.code,
                Reason="Voucher Acquirement",
                DestinationAccount=account)
            for bill_item in bill.line_items_bill.filter(is_deleted=False)
        ]

        if not order_lines:
            raise Fault(faultcode='InvalidParameter', faultstring=f'OrderKey "{query.OrderKey}" has no line items')

        order_details = OrderDetails(
            Currency=InvoiceConfig.default_currency_code,
            Lines=order_lines,
            OrderKey=bill.code,
            Reason="Voucher Acquirement",
            ServiceID=query.ServiceID,
            Status=OrderStatus.Active,
            TotalAmountDue=str(bill.amount_total)
        )

        return GetOrderDetailsResult(OrderDetails=order_details)

    @rpc(PaymentConfirmation.customize(min_occurs=1, max_occurs=1, nillable=False))
    def ConfirmOrderPayment(ctx, confirmation: PaymentConfirmation) -> None:
        _check_service_id(confirmation.ServiceID)
        bill = _get_order(confirmation.OrderKey)

        with transaction.atomic():
            for line in confirmation.Lines:
                line_amount = decimal.Decimal(line.Amount)
                bill_item = _get_order_line(bill, line.LineID)
                _check_amount_due(bill_item, line_amount)
                voucher = _get_voucher(bill_item)
                if voucher.status != WorkerVoucher.Status.ASSIGNED:
                    voucher.status = WorkerVoucher.Status.ASSIGNED
                    voucher.save(username=voucher.user_updated.username)

            if bill.status != Bill.Status.PAID:
                bill.status = Bill.Status.PAID
                bill.save(username=bill.user_updated.username)


_application = Application(
    [MpayService],
    tns=namespace,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)
_application.event_manager.add_listener('method_call', _validate_envelope)

mpay_app = DjangoApplication(_application)
mpay_app.event_manager.add_listener('wsgi_return', _add_envelope_header)
