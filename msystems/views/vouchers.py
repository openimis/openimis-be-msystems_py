import logging

from lxml import etree
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.fault import Fault
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase
from zeep.exceptions import SignatureVerificationFailed

from msystems.apps import MsystemsConfig
from msystems.soap.datetime import SoapDatetime
from msystems.xml_utils import add_signature, verify_signature, verify_timestamp, add_timestamp
from worker_voucher.models import WorkerVoucher
from msystems.soap.models import VoucherDetails, VouchersDetailsQuery, GetVouchersDetailsResult


namespace = 'https://mpay.gov.md'
logger = logging.getLogger(__name__)


def _get_vouchers(query: VouchersDetailsQuery):
    vouchers = WorkerVoucher.objects.filter(is_deleted=False)

    # Apply filters based on the query attributes
    if query.AssignedDate:
        vouchers = vouchers.filter(assigned_date=query.AssignedDate)

    if query.ExpiryDate:
        vouchers = vouchers.filter(expiry_date=query.ExpiryDate)

    if query.EmployerCode:
        vouchers = vouchers.filter(policyholder__code=query.EmployerCode)

    if query.WorkerNationalID:
        vouchers = vouchers.filter(insuree__chf_id=query.WorkerNationalID)

    if query.VoucherCode:
        vouchers = vouchers.filter(code=query.VoucherCode)

    if query.VoucherStatus:
        vouchers = vouchers.filter(status=query.VoucherStatus)

    return vouchers


def _log_rpc_call(ctx):
    input = ctx.transport.req.get('wsgi.input')
    action = ctx.transport.req.get('HTTP_SOAPACTION')
    if input:
        input.seek(0)
        data = input.read().decode("utf-8")
        logger.info(f"Method {action} called with:\n{data}\n")
        input.seek(0)


def _validate_envelope(ctx):
    root = ctx.in_document

    try:
        verify_timestamp(root)
    except ValueError as e:
        logger.error("Timestamp verification failed", exc_info=e)
        raise Fault(faultcode='InvalidRequest', faultstring=str(e))

    try:
        verify_signature(root, MsystemsConfig.voucher_config['client_certificate'])
    except SignatureVerificationFailed as e:
        logger.error("Envelope signature verification failed", exc_info=e)
        raise Fault(faultcode='InvalidRequest', faultstring='Envelope signature verification failed')


def _add_envelope_header(ctx):
    root = ctx.out_document

    add_timestamp(root)
    add_signature(root, MsystemsConfig.voucher_config['service_private_key'],
                  MsystemsConfig.voucher_config['service_certificate'])

    envelope = etree.tostring(ctx.out_document, pretty_print=True)
    logger.info(envelope.decode('utf-8'))
    ctx.out_string = [envelope]


class VoucherService(ServiceBase):
    @rpc(VouchersDetailsQuery.customize(min_occurs=1, max_occurs=1, nillable=False),
         _returns=GetVouchersDetailsResult.customize(min_occurs=1, max_occurs=1, nillable=False))
    def GetVouchersDetails(ctx, query: VouchersDetailsQuery) -> GetVouchersDetailsResult:
        vouchers = _get_vouchers(query)

        vouchers_details = []
        for voucher in vouchers:
            vouchers_details.append(VoucherDetails(
                AssignedDate=SoapDatetime.from_ad_date(voucher.assigned_date),
                ExpiryDate=SoapDatetime.from_ad_date(voucher.expiry_date),
                EmployerCode=str(voucher.policyholder.code) if voucher.policyholder else None,
                WorkerNationalID=str(voucher.insuree.chf_id) if voucher.insuree else None,
                VoucherCode=str(voucher.code),
                VoucherStatus=str(voucher.status),
            ))

        if not vouchers_details:
            raise Fault(faultcode='InvalidParameter',
                        faultstring=f'Given criteria has no associated vouchers')

        ret = GetVouchersDetailsResult(VouchersDetails=vouchers_details)
        return ret


def _error_handler_function(ctx, *args, **kwargs):
    logger.error("Spyne error", exc_info=ctx.in_error)


_application = Application(
    [VoucherService],
    tns=namespace,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)
_application.event_manager.add_listener('method_call', _validate_envelope)
_application.event_manager.add_listener('method_exception_object', _error_handler_function)

voucher_app = DjangoApplication(_application)
voucher_app.event_manager.add_listener('wsgi_call', _log_rpc_call)
voucher_app.event_manager.add_listener('wsgi_return', _add_envelope_header)
