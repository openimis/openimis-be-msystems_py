# This repository holds the files of the openIMIS Backend MSystems (Moldova) Integration reference module.

# Voucher Service Documentation

## Overview

The Voucher Service provides a SOAP-based interface for querying voucher details. This service allows you to retrieve information about vouchers based on various filtering criteria. 


## Voucher Data Structures

### VoucherStatus Enumeration

| **Name**           | **Description**                                           |
|--------------------|-----------------------------------------------------------|
| `Assigned`         | Voucher is assigned to a worker but not yet paid.         |
| `AwaitingPayment`  | Voucher is assigned and awaiting payment.                 |
| `Canceled`         | Voucher has been canceled and is no longer valid.         |
| `Closed`           | Voucher has been used or closed.                          |
| `Expired`          | Voucher has expired and is no longer valid.               |
| `Unassigned`       | Voucher has not been assigned to any worker.              |

### VoucherDetails Complex Model

| **Field Name**        | **Type**            | **Description**                                    |
|-----------------------|---------------------|----------------------------------------------------|
| `AssignedDate`        | `DateTime`          | The date when the voucher was assigned. May be null if unassigned. |
| `EmployerCode`        | `Unicode`           | The code representing the employer.                |
| `ExpiryDate`          | `DateTime`          | The expiry date of the voucher.                    |
| `WorkerNationalID`    | `Unicode`           | The national ID of the worker to whom the voucher is assigned. May be null if unassigned. |
| `VoucherCode`         | `Unicode`           | The unique code of the voucher.                    |
| `VoucherStatus`       | `VoucherStatus`     | The current status of the voucher.                 |

### GetVouchersDetailsResult Complex Model

| **Field Name**        | **Type**            | **Description**                                    |
|-----------------------|---------------------|----------------------------------------------------|
| `VouchersDetails`     | `Array<VoucherDetails>` | A list of voucher details matching the query criteria. |

---

## XML Example

Here’s an example of the SOAP response XML:

```xml
<tns:GetVouchersDetailsResponse>
    <tns:GetVouchersDetailsResult>
        <tns:VouchersDetails>
            <tns:VoucherDetails>
                <tns:AssignedDate>2024-08-20T00:00:00Z</tns:AssignedDate>
                <tns:EmployerCode>CC</tns:EmployerCode>
                <tns:ExpiryDate>2024-09-20T00:00:00Z</tns:ExpiryDate>
                <tns:WorkerNationalID>111111111111</tns:WorkerNationalID>
                <tns:VoucherCode>06731689-c124-4f64-bb16-93579a7f80af</tns:VoucherCode>
                <tns:VoucherStatus>AwaitingPayment</tns:VoucherStatus>
            </tns:VoucherDetails>
            <!-- More VoucherDetails elements can follow -->
        </tns:VouchersDetails>
    </tns:GetVouchersDetailsResult>
</tns:GetVouchersDetailsResponse>
```
## Data Mappings

### Voucher Status Mapping

#### System to SOAP
 **System Status**                       | **SOAP VoucherStatus** |
|-----------------------------------------|------------------------|
| `WorkerVoucher.Status.ASSIGNED`         | `Assigned`             |
| `WorkerVoucher.Status.AWAITING_PAYMENT` | `AwaitingPayment`      |
| `WorkerVoucher.Status.CANCELED`         | `Canceled`             |
| `WorkerVoucher.Status.CLOSED`           | `Closed`               |
| `WorkerVoucher.Status.EXPIRED`          | `Expired`              |
| `WorkerVoucher.Status.UNASSIGNED`       | `Unassigned`           |

#### SOAP to System

| **SOAP VoucherStatus** | **System Status**                       |
|------------------------|-----------------------------------------|
| `Assigned`             | `WorkerVoucher.Status.ASSIGNED`         |
| `AwaitingPayment`      | `WorkerVoucher.Status.AWAITING_PAYMENT` |
| `Canceled`             | `WorkerVoucher.Status.CANCELED`         |
| `Closed`               | `WorkerVoucher.Status.CLOSED`           |
| `Expired`              | `WorkerVoucher.Status.EXPIRED`          |
| `Unassigned`           | `WorkerVoucher.Status.UNASSIGNED`       |

---

## Query Filters

The `VouchersDetailsQuery` complex model allows filtering vouchers based on various criteria. Below are the available filters:

| **Filter Name**       | **Type**      | **Required** | **Description**                                                      |
|-----------------------|---------------|--------------|----------------------------------------------------------------------|
| `AssignedDate`        | `DateTime`    | No           | Filters vouchers assigned on a specific date.                        |
| `ExpiryDate`          | `DateTime`    | No           | Filters vouchers expiring on a specific date.                        |
| `EmployerCode`        | `Unicode`     | No           | Filters vouchers by the employer's code.                             |
| `WorkerNationalID`    | `Unicode`     | No           | Filters vouchers by the worker's national ID.                        |
| `VoucherCode`         | `Unicode`     | No           | Filters vouchers by the unique voucher code.                         |
| `VoucherStatus`       | `VoucherStatus`| No           | Filters vouchers by their status (e.g., Assigned, AwaitingPayment).   |

---

## Example Filter Usage

### Example Request

```xml
   <soap-env:Body>
      <ns0:GetVouchersDetails xmlns:ns0="https://mpay.gov.md">
         <ns0:query>
            <ns0:AssignedDate>2024-08-20T00:00:00Z</ns0:AssignedDate>
            <ns0:EmployerCode>CC</ns0:EmployerCode>
            <ns0:VoucherStatus>AwaitingPayment</ns0:VoucherStatus>
         </tns:query>
      </ns0:GetVouchersDetails>
   </soapenv:Body>
```

### Example Response

```xml
<tns:GetVouchersDetailsResponse xmlns:tns="https://mpay.gov.md">
    <tns:GetVouchersDetailsResult>
        <tns:VouchersDetails>
            <tns:VoucherDetails>
                <tns:AssignedDate>2024-08-20T00:00:00Z</tns:AssignedDate>
                <tns:EmployerCode>CC</tns:EmployerCode>
                <tns:ExpiryDate>2024-09-20T00:00:00Z</tns:ExpiryDate>
                <tns:WorkerNationalID>111111111111</tns:WorkerNationalID>
                <tns:VoucherCode>06731689-c124-4f64-bb16-93579a7f80af</tns:VoucherCode>
                <tns:VoucherStatus>AwaitingPayment</tns:VoucherStatus>
            </tns:VoucherDetails>
            <!-- Additional VoucherDetails elements -->
        </tns:VouchersDetails>
    </tns:GetVouchersDetailsResult>
</tns:GetVouchersDetailsResponse>
```

### Explanation: 
The above request fetches all vouchers that meet the following criteria:
* Assigned on `2024-08-20`.
* Associated with the employer code `CC`.
* Have a status of `AwaitingPayment`.

## Error Handling

If no vouchers match the provided criteria, the service will return a SOAP fault.

### Example Fault Response

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <soapenv:Fault>
         <faultcode>soapenv:Client</faultcode>
         <faultstring>Given criteria has no associated vouchers</faultstring>
      </soapenv:Fault>
   </soapenv:Body>
</soapenv:Envelope>
```

### Fault Details:
* `faultcode`: Indicates the fault type. In this case, soapenv:Client signifies a client-side error due to invalid request parameters.
* `faultstring`: Provides a descriptive message about the error encountered.

## Notes
* All date and time values should be in ISO 8601 format and UTC timezone.
* When multiple filters are provided, the service performs an AND operation, returning vouchers that satisfy all criteria.
* The VoucherStatus filter should use one of the predefined enumeration values:
  - Assigned
  - AwaitingPayment
  - Canceled
  - Closed
  - Expired
  - Unassigned

## Additional Examples

### Filtering by `VoucherCode`
**Request:**
```xml
<ns0:GetVouchersDetails xmlns:ns0="https://mpay.gov.md">
  <ns0:query>
    <ns0:VoucherCode>123e4567-e89b-12d3-a456-426614174000</ns0:VoucherCode>
  </ns0:query>  
</ns0:GetVouchersDetails>
```
**Description:**
This request retrieves the details of a specific voucher identified by the VoucherCode `123e4567-e89b-12d3-a456-426614174000`.

### Filtering by WorkerNationalID and ExpiryDate
**Request:**
```xml
<ns0:GetVouchersDetails xmlns:ns0="https://mpay.gov.md">
  <ns0:query>
    <ns0:WorkerNationalID>111111111111</ns0:WorkerNationalID>
    <ns0:ExpiryDate>2024-12-31T00:00:00Z</ns0:ExpiryDate>
  </ns0:query>  
</ns0:GetVouchersDetails>
```
**Description:**
This request fetches all vouchers assigned to the worker with the National ID `111111111111` that are set to expire on `2024-12-31`.

### Filtering by WorkerNationalID and VoucherCode
**Request:**
```xml
<ns0:GetVouchersDetails xmlns:ns0="https://mpay.gov.md">
  <ns0:query>
    <ns0:WorkerNationalID>111111111111</ns0:WorkerNationalID>
    <ns0:VoucherCode>123e4567-e89b-12d3-a456-426614174000</ns0:VoucherCode>
  </ns0:query>  
</ns0:GetVouchersDetails>
```
**Description:**
This request retrieves the details for a voucher identified by VoucherCode `123e4567-e89b-12d3-a456-426614174000`, assigned to the worker with National ID `111111111111`.

### Filtering by Status and ExpiryDate
**Request:**
```xml
<ns0:GetVouchersDetails xmlns:ns0="https://mpay.gov.md">
  <ns0:query>
    <ns0:Status>Expired</ns0:Status>
    <ns0:ExpiryDate>2023-12-31T00:00:00Z</ns0:ExpiryDate>
  </ns0:query>  
</ns0:GetVouchersDetails>
```
**Description:**
This request fetches all vouchers that are `Expired` as of `2023-12-31`.