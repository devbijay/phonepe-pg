import base64
import hashlib
import json
import requests
from pydantic import BaseModel, Field


class RefundTxn(BaseModel):
    txn_user_id: str = Field(..., description="The User ID of the merchant user.")
    merchant_order_id: str = Field(..., description="The ID of the merchant transaction.")
    phonepe_txn_id: str = Field(..., description="The ID of the phonepe transaction.")
    amount: int = Field(..., gt=0, description="The transaction amount in paise.")


class PhonePe:
    def __init__(self, merchant_id: str, phone_pe_salt: str, phone_pe_host: str, redirect_url: str, webhook_url: str,
                 phone_pe_salt_index: int = 1, redirect_mode="POST"):
        """
           Initialize the PhonePe class.

           Args:
               merchant_id (str): The ID of the merchant.
               phone_pe_salt (str): The PhonePe salt.
               redirect_url (str): The redirect URL.
               webhook_url (str): The webhook URL.
               phone_pe_salt_index (int, optional): The PhonePe salt index. Defaults to 1.
               redirect_mode (str, optional): The redirect mode. Defaults to "GET". Valid Values "REDIRECT/POST"
        """

        self.merchant_id = merchant_id
        self.phone_pe_salt = phone_pe_salt
        self.phone_pe_salt_index = phone_pe_salt_index
        self.phone_pe_host = phone_pe_host
        self.redirect_url = redirect_url
        self.webhook_url = webhook_url
        self.redirect_mode = redirect_mode

    @staticmethod
    def sha256_encode(string):
        """
            Calculate the SHA256 hash of a string.

            Args:
                string (str): The input string.

            Returns:
                str: The SHA256 hash of the string.
        """
        sha256_hash = hashlib.sha256()
        encoded_string = string.encode('utf-8')
        sha256_hash.update(encoded_string)
        return sha256_hash.hexdigest()

    def create_order(self, order_id, amount, user):
        """
            Create the checksum & order_payload for the PhonePe transaction.

            Args:
                order_id (str): The ID of the order.
                amount (float): The transaction amount.
                user (str): The user ID.

            Returns:
                list: A list containing the checksum and the base64-encoded payload.
        """

        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": order_id,
            "merchantUserId": user,
            "amount": int(amount),
            "redirectUrl": self.redirect_url,
            "redirectMode": self.redirect_mode,
            "callbackUrl": self.webhook_url,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }
        json_payload = json.dumps(payload)
        base64_encoded = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')

        check_sum = f'{self.sha256_encode(f"{base64_encoded}/pg/v1/pay{self.phone_pe_salt}")}###{self.phone_pe_salt_index}'

        return [check_sum, base64_encoded]

    def create_phone_pe_txn(self, check_sum: str, encoded_order_payload: str):
        """
            Create the PhonePe transaction link.

            Args:
                check_sum (str): The checksum.
                encoded_order_payload (str): The base64-encoded order payload.

            Returns:
                dict: The response JSON if successful, None otherwise.
        """
        payload = {"request": encoded_order_payload}
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-VERIFY": check_sum
        }
        try:
            response = requests.post(f"{self.phone_pe_host}/pg/v1/pay", json=payload, headers=headers)
            return response.json()
        except Exception:
            return None

    def check_txn_status(self, merchant_txn_id):
        """
            Checks the status of a PhonePe transaction.

            Args:
                merchant_txn_id: The merchant transaction ID.

            Returns:
                The status of the transaction, or None if the transaction could not be found.
        """
        base_url = f"{self.phone_pe_host}/pg/v1/status/{self.merchant_id}/{merchant_txn_id}"

        sha_header = f'{self.sha256_encode(f"/pg/v1/status/{self.merchant_id}/{merchant_txn_id}{self.phone_pe_salt}")}###{self.phone_pe_salt_index}'
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-VERIFY": sha_header,
            "X-MERCHANT-ID": self.merchant_id
        }


        print(headers)
        try:
            response = requests.get(base_url, headers=headers)
            return response.json()
        except Exception:
            return None

    def refund_txn(self, refund_txn: RefundTxn):
        """
            Refunds a PhonePe transaction.

            Args:
                refund_txn: The refund transaction object.

            Returns:
                The status of the refund, or None if the refund could not be processed.
        """
        refund_payload = {
            "merchantId": self.merchant_id,
            "merchantUserId": refund_txn.txn_user_id,
            "originalTransactionId": refund_txn.merchant_order_id,
            "merchantTransactionId": refund_txn.phonepe_txn_id,
            "amount": int(refund_txn.amount),
            "callbackUrl": self.webhook_url
        }
        json_payload = json.dumps(refund_payload)
        base64_encoded = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')
        sha_header = f'{self.sha256_encode(f"{base64_encoded}/pg/v1/refund{self.phone_pe_salt}")}###{self.phone_pe_salt_index}'

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-VERIFY": sha_header,
        }
        print(refund_payload)
        payload = {"request": base64_encoded}
        url = f"{self.phone_pe_host}/pg/v1/refund"
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception:
            return None

    def verify_vpa(self, vpa_address):
        """
            Validates a PhonePe VPA address.

            Args:
                vpa_address: The VPA address to validate.

            Returns:
                The status of the VPA validation, or None if the VPA could not be validated.
        """
        vpa_payload = {
            "merchantId": self.merchant_id,
            "vpa": vpa_address
        }
        json_payload = json.dumps(vpa_payload)
        base64_encoded = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')
        sha_header = f'{self.sha256_encode(f"{base64_encoded}/pg/v1/vpa/validate{self.phone_pe_salt}")}###{self.phone_pe_salt_index}'
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": sha_header,
        }
        payload = {"request": base64_encoded}
        try:
            response = requests.post(f"{self.phone_pe_host}/pg/v1/vpa/validate", json=payload, headers=headers)
            return response.json()
        except Exception:
            return None
