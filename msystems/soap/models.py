from spyne.model.primitive import Unicode, DateTime, Decimal, Boolean
from spyne.model.complex import ComplexModel, Array
from spyne.model.enum import Enum

namespace = 'https://mpay.gov.md'

CurrencyCode = Enum('MDL', 'EUR', 'USD', type_name='Currency')
CustomerType = Enum('Unspecified', 'Person', 'Organization', type_name='CustomerType')
OrderStatus = Enum('Active', 'PartiallyPaid', 'Paid', 'Completed', 'Expired', 'Canceled', 'Refunding',
                   'Refunded', type_name='OrderStatus')
PropertyType = Enum('string', 'idn', 'tc', type_name='Type')


class OrderProperty(ComplexModel):
    namespace = namespace
    __type_name__ = 'OrderProperty'

    DisplayName = Unicode.customize(min_occurs=0, max_occurs=1, max_len=36, nillable=False)
    Modifiable = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    Name = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Required = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    Type = PropertyType.customize(min_occurs=0, max_occurs=1, nillable=False, default=PropertyType.string)
    Value = Unicode.customize(min_occurs=1, max_occurs=1, max_len=255, nillable=False)


class PaymentAccount(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'PaymentAccount'

    BankAccount = Unicode.customize(min_occurs=1, max_occurs=1, max_len=24, nillable=False)
    BankCode = Unicode.customize(min_occurs=1, max_occurs=1, max_len=20, nillable=False)
    BankFiscalCode = Unicode.customize(min_occurs=1, max_occurs=1, max_len=20, nillable=False)
    BeneficiaryName = Unicode.customize(min_occurs=1, max_occurs=1, max_len=60, nillable=False)
    ConfigurationCode = Unicode.customize(min_occurs=0, max_occurs=1, max_len=36, nillable=False)


class OrderDetailsQuery(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'OrderDetailsQuery'

    Language = Unicode.customize(min_occurs=0, max_occurs=1, max_len=2, nillable=False, default='ro')
    OrderKey = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    ServiceID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)


class OrderLine(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'OrderLine'

    AllowAdvancePayment = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    AllowPartialPayment = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    AmountDue = Decimal.customize(min_occurs=0, max_occurs=1, nillable=False)
    DestinationAccount = PaymentAccount.customize(min_occurs=1, max_occurs=1, nillable=False)
    LineID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Properties = (Array(OrderProperty.customize(min_occurs=0, max_occurs="unbounded", nillable=False))
                  .customize(min_occurs=0, max_occurs=1, nillable=False))
    Reason = Unicode.customize(min_occurs=1, max_occurs=1, max_len=50, nillable=False)


class OrderDetails(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'OrderDetails'

    AllowAdvancePayment = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    AllowPartialPayment = Boolean.customize(min_occurs=0, max_occurs=1, nillable=False, default=False)
    Currency = CurrencyCode.customize(min_occurs=1, max_occurs=1, nillable=False)
    CustomerID = Unicode.customize(min_occurs=0, max_occurs=1, max_len=13, nillable=False)
    CustomerName = Unicode.customize(min_occurs=1, max_occurs=1, max_len=60, nillable=False)
    CustomerType = CustomerType.customize(min_occurs=1, max_occurs=1, nillable=False)
    DueDate = DateTime.customize(min_occurs=0, max_occurs=1, nillable=False)
    IssuedAt = DateTime.customize(min_occurs=0, max_occurs=1, nillable=False)
    Lines = (Array(OrderLine.customize(min_occurs=1, max_occurs="unbounded", nillable=False))
             .customize(min_occurs=1, max_occurs=1, nillable=False))
    OrderKey = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Properties = (Array(OrderProperty.customize(min_occurs=0, max_occurs="unbounded", nillable=False))
                  .customize(min_occurs=0, max_occurs=1, nillable=False))
    Reason = Unicode.customize(min_occurs=1, max_occurs=1, max_len=50, nillable=False)
    ServiceID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Status = OrderStatus.customize(min_occurs=1, max_occurs=1, nillable=False)
    TotalAmountDue = Decimal.customize(min_occurs=0, max_occurs=1, nillable=False)


class GetOrderDetailsResult(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'GetOrderDetailsResult'

    OrderDetails = OrderDetails.customize()


class PaymentProperty(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'PaymentProperty'

    Name = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Value = Unicode.customize(min_occurs=0, max_occurs=1, max_len=255, nillable=False)


class PaymentConfirmationLine(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'PaymentConfirmationLine'

    Amount = Decimal.customize(min_occurs=1, max_occurs=1, nillable=False)
    DestinationAccount = PaymentAccount.customize(min_occurs=1, max_occurs=1, nillable=False)
    LineID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Properties = (Array(PaymentProperty.customize(min_occurs=0, max_occurs="unbounded", nillable=False))
                  .customize(min_occurs=0, max_occurs=1, nillable=False))


class PaymentConfirmation(ComplexModel):
    __namespace__ = namespace
    __type_name__ = 'PaymentConfirmation'

    Currency = CurrencyCode.customize(min_occurs=1, max_occurs=1, nillable=False)
    InvoiceID = Unicode.customize(min_occurs=0, max_occurs=1, max_len=36, nillable=False)
    Lines = Array(PaymentConfirmationLine.customize(min_occurs=1, max_occurs="unbounded", nillable=False))
    OrderKey = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    PaidAt = DateTime.customize(min_occurs=1, max_occurs=1, nillable=False)
    PaymentID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    Properties = (Array(PaymentProperty.customize(min_occurs=0, max_occurs="unbounded", nillable=False))
                  .customize(min_occurs=0, max_occurs=1, nillable=False))
    ServiceID = Unicode.customize(min_occurs=1, max_occurs=1, max_len=36, nillable=False)
    TotalAmount = Decimal.customize(min_occurs=1, max_occurs=1, nillable=False)
