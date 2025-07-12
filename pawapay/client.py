import json
import hmac
import time
import uuid
import hashlib
import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Optional, Dict, Any, List


from models import (
    DepositRequest,
    PayoutRequest,
    DepositResponse,
    PayoutResponse,
    Correspondent,
    PawaPayError,
    TransactionStatus,
    Payer,
    Recipient
)
from config import PawaPayConfig
from exceptions import PawaPayException, PawaPayAPIException


class PawaPayClient:
    """PawaPay API client for mobile money payments"""

    def __init__(self, config: PawaPayConfig):
        self.config = config
        self.config.validate()

        # Setup HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())

    def _calculate_signature(self, body: str) -> str:
        """Calculate SHA-256 hash of request body"""
        return hashlib.sha256(body.encode()).hexdigest()

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to PawaPay API"""
        url = f"{self.config.base_url}{endpoint}"

        # Prepare request data
        json_data = json.dumps(data) if data else None

        # Add signature headers if enabled
        headers = {}
        if self.config.enable_signed_requests and json_data:
            headers['Content-Digest'] = f'sha-256=:{self._calculate_signature(json_data)}:'

        try:
            response = self.session.request(
                method=method,
                url=url,
                data=json_data,
                headers=headers,
                timeout=self.config.timeout
            )

            # Handle response
            if response.status_code in [200, 201, 202]:
                return response.json() if response.content else {}
            else:
                error_data = response.json() if response.content else {}
                error = PawaPayError.from_dict(error_data)
                raise PawaPayAPIException(
                    f"API Error: {error.error_message}",
                    status_code=response.status_code,
                    error_code=error.error_code,
                    details=error.details
                )

        except requests.exceptions.RequestException as e:
            raise PawaPayException(f"Request failed: {str(e)}")

    def get_active_configuration(self) -> Dict[str, Any]:
        """Get active configuration including available correspondents"""
        return self._make_request('GET', '/active-conf')

    def get_correspondents(self) -> List[Correspondent]:
        """Get list of available correspondents (MMOs) from all countries"""
        config = self.get_active_configuration()
        correspondents = []

        # Correspondents are grouped by country in the response
        for country_data in config.get('countries', []):
            for correspondent_data in country_data.get('correspondents', []):
                # Add country info to correspondent data if needed
                correspondent_data['country'] = country_data['country']
                correspondents.append(Correspondent.from_dict(correspondent_data))

        return correspondents

    def get_correspondents_by_country(self, country_code: str) -> List[Correspondent]:
        """Get correspondents for a specific country"""
        config = self.get_active_configuration()
        correspondents = []

        for country_data in config.get('countries', []):
            if country_data['country'] == country_code:
                for correspondent_data in country_data.get('correspondents', []):
                    correspondent_data['country'] = country_code
                    correspondents.append(Correspondent.from_dict(correspondent_data))
                break

        return correspondents

    def predict_correspondent(self, msisdn: str) -> Optional[str]:
        """Predict correspondent for a given phone number"""
        try:
            response = self._make_request(
                'POST',
                '/v1/predict-correspondent',
                data={"msisdn": msisdn}
            )
            return response.get('correspondent')
        except PawaPayAPIException:
            return None

    def request_deposit(
        self,
        amount: str,
        currency: str,
        phone_number: str,
        correspondent: Optional[str] = None,
        statement_description: Optional[str] = None
    ) -> DepositResponse:
        """Request a deposit (payment from customer)"""

        # Predict correspondent if not provided
        if not correspondent:
            correspondent = self.predict_correspondent(phone_number)
            if not correspondent:
                raise PawaPayException("Could not predict correspondent for phone number")

        # Create deposit request
        deposit_request = DepositRequest(
            deposit_id=self._generate_request_id(),
            amount=amount,
            currency=currency,
            correspondent=correspondent,
            payer=Payer(
                type="MSISDN",
                address={"value": phone_number}
            ),
            customer_timestamp=datetime.utcnow().isoformat() + "Z",
            statement_description=statement_description
        )

        response_data = self._make_request(
            'POST',
            '/deposits',
            deposit_request.to_dict()
        )

        if response_data.get('status') == 'REJECTED':
            rejection_reason = response_data.get('rejectionReason', {})
            raise ValueError(
                f"Deposit was rejected."
                f"Code: {rejection_reason.get('rejectionCode')}, "
                f"Message: {rejection_reason.get('rejectionMessage')}"
            )

        response_data["amount"] = amount
        response_data["currency"] = currency
        response_data["correspondent"] = correspondent
        response_data["payer"] = Payer(
            type="MSISDN",
            address={"value": phone_number}
        ).to_dict()

        return DepositResponse.from_dict(response_data)

    def check_deposit_status(self, deposit_id: str) -> DepositResponse:
        """Check status of a deposit"""
        response_data = self._make_request('GET', f'/deposits/{deposit_id}')
        return DepositResponse.from_dict(response_data[0])

    def request_payout(
        self,
        amount: str,
        currency: str,
        country: str,
        phone_number: str,
        correspondent: Optional[str] = None,
        statement_description: Optional[str] = None
    ) -> PayoutResponse:
        """Request a payout (payment to recipient)"""

        # Predict correspondent if not provided
        if not correspondent:
            correspondent = self.predict_correspondent(phone_number)
            if not correspondent:
                raise PawaPayException("Could not predict correspondent for phone number")

        # Create payout request
        payout_request = PayoutRequest(
            payout_id=self._generate_request_id(),
            amount=amount,
            country=country,
            currency=currency,
            correspondent=correspondent,
            recipient=Recipient(type="MSISDN", value=phone_number),
            customer_timestamp=datetime.utcnow().isoformat() + "Z",
            statement_description=statement_description
        )

        response_data = self._make_request('POST', '/payouts', payout_request.to_dict())

        if response_data.get('status') == 'REJECTED':
            rejection_reason = response_data.get('rejectionReason', {})
            raise ValueError(
                f"Payout was rejected."
                f"Code: {rejection_reason.get('rejectionCode')}, "
                f"Message: {rejection_reason.get('rejectionMessage')}"
            )

        response_data["amount"] = amount
        response_data["currency"] = currency
        response_data["correspondent"] = correspondent
        response_data["recipient"] = Recipient(
            type="MSISDN",
            value=phone_number
        ).to_dict()

        return PayoutResponse.from_dict(response_data)

    def check_payout_status(self, payout_id: str) -> PayoutResponse:
        """Check status of a payout"""
        response_data = self._make_request('GET', f'/payouts/{payout_id}')
        return PayoutResponse.from_dict(response_data[0])

    def refund_deposit(self, deposit_id: str) -> Dict[str, Any]:
        """Refund a completed deposit"""
        return self._make_request('POST', f'/v1/deposits/{deposit_id}/refund')

    def resend_callback(self, transaction_id: str, transaction_type: str) -> Dict[str, Any]:
        """Resend callback for a transaction"""
        endpoint = f'/v1/{transaction_type}s/{transaction_id}/resend-callback'
        return self._make_request('POST', endpoint)

    def validate_callback(self, payload: str, signature: str) -> bool:
        """Validate callback signature"""
        if not self.config.callback_secret:
            return False

        expected_signature = hmac.new(
            self.config.callback_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def create_payment_page_deposit(
        self,
        amount: str,
        currency: str,
        return_url: str,
        statement_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create deposit via payment page"""
        data = {
            "depositId": self._generate_request_id(),
            "amount": amount,
            "currency": currency,
            "returnUrl": return_url,
            "customerTimestamp": datetime.utcnow().isoformat() + "Z"
        }

        if statement_description:
            data["statementDescription"] = statement_description

        return self._make_request('POST', '/v1/payment-page/deposits', data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


# Convenience function to create client from environment
def create_client() -> PawaPayClient:
    """Create PawaPay client from environment variables"""
    config = PawaPayConfig.from_env()
    return PawaPayClient(config)
