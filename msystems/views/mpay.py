import decimal
import logging

from lxml import etree
from django.db import transaction
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.fault import Fault
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase
from zeep.exceptions import SignatureVerificationFailed

from invoice.apps import InvoiceConfig
from invoice.models import Bill
from msystems.apps import MsystemsConfig
from msystems.soap.models import OrderDetailsQuery, GetOrderDetailsResult, OrderLine, OrderDetails, \
    PaymentConfirmation, PaymentAccount, OrderStatus
from msystems.xml_utils import add_signature, verify_signature, verify_timestamp, add_timestamp
from worker_voucher.models import WorkerVoucher

namespace = 'https://zilieri.gov.md'
logger = logging.getLogger(__name__)

_order_status_map = {
    Bill.Status.DRAFT: OrderStatus.Expired,
    Bill.Status.VALIDATED: OrderStatus.Active,
    Bill.Status.PAID: OrderStatus.Paid,
    Bill.Status.CANCELLED: OrderStatus.Canceled,
    Bill.Status.DELETED: OrderStatus.Canceled,
    Bill.Status.SUSPENDED: OrderStatus.Canceled,
    Bill.Status.UNPAID: OrderStatus.Expired,
    Bill.Status.RECONCILIATED: OrderStatus.Paid
}


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

    try:
        verify_timestamp(root)
    except ValueError as e:
        raise Fault(faultcode='InvalidRequest', faultstring=str(e))

    try:
        verify_signature(root, MsystemsConfig.mpay_config['mpay_certificate'])
    except SignatureVerificationFailed:
        raise Fault(faultcode='InvalidRequest', faultstring=f'Envelope signature verification failed')


def _add_envelope_header(ctx):
    root = ctx.out_document

    add_timestamp(root)
    add_signature(root, MsystemsConfig.mpay_config['service_private_key'],
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
            Status=_order_status_map[bill.status],
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
