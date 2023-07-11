# PhonePe Payment Gateway Python Package

This Python package provides a simple interface to the PhonePe Payment Gateway. It can be used to create PhonePe payment links, check the status of PhonePe transactions, and refund PhonePe transactions.

## Installation

To install the package, run the following command:

```
pip install phonepe
```

## Usage

#### The following code shows how to create a PhonePe payment link:
* Initiate PhonePe Object

```python
from phonepe import PhonePe

phonepe = PhonePe("MERCHANT_ID", "PHONEPE_SALT", "PHONEPE_HOST", "REDIRECT_URL", "WEBHOOK_URL")
```

```csv
Args:
   merchant_id (str): The ID of the merchant.
   phone_pe_salt (str): The PhonePe salt.
   redirect_url (str): The redirect URL.
   webhook_url (str): The webhook URL.
   phone_pe_salt_index (int, optional): The PhonePe salt index. Defaults to 1.
   redirect_mode (str, optional): The redirect mode. Defaults to "GET". Valid Values "GET/POST"
```

* Create CheckSum And base64 encoded payment data
```python
check_sum, encoded_order_payload = phonepe.create_order("ORDER_ID", 100, "USER_ID")

#Create Transaction Link
phonepe_txn = phonepe.create_phone_pe_txn(check_sum, encoded_order_payload)

print(phonepe_txn)
```
* Note: Please Store The Checksum If You Are Updating The Transaction Status Via Webhook Callback
* The payload that is going to be sent to the merchant on the specified callback URL will have a base64 encoded JSON.
* Upon base64 decoding the response, you should get a JSON with a format similar to the response returned by transaction status API.
Following are the response headers sent with a callback.

* Please follow [this documentation](http://developer.phonepe.com/v1/reference/server-to-server-callback-5) if you are updating the paymenty status via  
webhook

```csv
Args:
    order_id (str): The ID of the order.
    amount (int): The transaction amount in paise.
    user (str): The user ID of the payment maker.
```
#### Example Response:
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "Your request has been successfully completed.",
  "data": {
    "merchantId": "MERCHANTUAT",
    "merchantTransactionId": "b7aa2cc7-cc5e-4d71-b98f-63ebf549010c",
    "instrumentResponse": {
      "type": "PAY_PAGE",
      "redirectInfo": {
        "url": "https://mercury-uat.phonepe.com/transact/pg?token=NGVjMzhjOWMzMGI5ODI2OWMwYmQ2MzUzYWE2ZDYzZGM0M2M0NjZkNjVjMWRmNzlmODk1YWEwNjViMTUwNjYyOTI4NDY1OWExYzNmMjQzNjYzZjgxOTQzYjVjMGUyMmYyZGZhMTg5ODRlZDM2MzEzNWYyZDViOTdkZmU2NjFjOGU3ZTdiMzNlNzpmM2ZkZDYwY2JmNGFiYTUxM2Y3OGJhNGVjOTQ5OWU1NQ",
        "method": "GET"
      }
    }
  }
}
```
You can use the `phonepe_txn['data']['instrumentResponse']['redirectInfo']['url']` to access the hosted checkout link
### Check Transaction Status

The following code shows how to check the status of a PhonePe transaction:

```python

status = phonepe.check_txn_status("MERCHANT_TXN_ID")

print(status)
```
#### Example Response:
```json
{
  "success": true,
  "code": "PAYMENT_SUCCESS",
  "message": "Your request has been successfully completed.",
  "data": {
    "merchantId": "FKRT",
    "merchantTransactionId": "MT7850590068188104",
    "transactionId": "T2111221437456190170379",
    "amount": 100,
    "paymentState": "COMPLETED",
    "responseCode": "PAYMENT_SUCCESS",
    "paymentInstrument": {
      "type": "UPI",
      "utr": "206378866112"
    }
  }
}
```

* S2S and Check Status API Handling

Once the customer is redirected back to the merchant website/app, merchants should check with their server if they have received the Server-to-Server Callback response. If not, it is mandatory to make a Transaction Status API check with PhonePe backend systems to know the actual status of the payment and, then accordingly process the result.

The payment status can be Success, Failed or Pending. When Pending, merchants should retry until the status changes to Success or Failed.

```html
Check Status API - Reconciliation [MANDATORY]

If the payment status is Pending, then Check Status API should be called in the following interval:
The first status check at 20-25 seconds post transaction start, then
Every 3 seconds once for the next 30 seconds,
Every 6 seconds once for the next 60 seconds,
Every 10 seconds for the next 60 seconds,
Every 30 seconds for the next 60 seconds, and then
Every 1 min until timeout (15 mins).
```
#### Refund A Transaction

```python
from phonepe import  RefundTxn

refund_txn = RefundTxn(
    txn_user_id="USER_ID",
    merchant_order_id="ORDER_ID",
    phonepe_txn_id="PHONEPE_TXN_ID",
    amount=100, ##in paise
)

status = phonepe.refund_txn(refund_txn)

print(status)
```
* Example Response:

```json
{
  "success": true,
  "code": "PAYMENT_SUCCESS",
  "message": "Your request has been successfully completed.",
  "data": {
    "merchantId": "MERCHANTUAT",
    "merchantTransactionId": "ROD620471739210623",
    "transactionId": "TR620471739210623",
    "amount": 10000,
    "state": "COMPLETED",
    "responseCode": "SUCCESS"
  }
}
```

#### Full Example
```python
from phonepe import PhonePe
from phonepe import RefundTxn

phonepe = PhonePe(
    merchant_id="PGTESTPAYUAT",
    phone_pe_salt="099eb0cd-02cf-4e2a-8aca-3e6c6aff0399",
    phone_pe_host="https://api-preprod.phonepe.com/apis/pg-sandbox",
    redirect_url="https://webhook.site/42fb84f2-1831-4467-9199-6bf0b839dc69",
    webhook_url="https://webhook.site/42fb84f2-1831-4467-9199-6bf0b839dc69"
)

# Create PhonePe Order
checksum, txn_data = phonepe.create_order("OTGTRT156", 1000, "bijay")
resp = phonepe.create_phone_pe_txn(checksum, txn_data)
payment_link = resp["data"]["instrumentResponse"]["redirectInfo"]["url"]

# Check Transaction Status
txn_status = phonepe.check_txn_status(resp['data']['merchantTransactionId'])

# Refund PhonePe Order
refund = RefundTxn(txn_user_id="bijay", merchant_order_id="OTGTRT156", phonepe_txn_id="T2307112141199670477007",
                   amount=1000)
ref_resp = phonepe.refund_txn(refund)

```

For more information, please see the official [documentation](https://developer.phonepe.com/v1/reference/pay-api-1).


I hope this is helpful! Let me know if you have any other questions.
```
Pending Feature
* Subscription Module
* Submerchant Onboarding