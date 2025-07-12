from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


class TransactionStatus(Enum):
    """Transaction status enumeration"""
    # The transaction request has been accepted by pawaPay for processing
    ACCEPTED = "ACCEPTED"

    # The transaction request has been accepted but enqueued for processing later (typically when MMO is experiencing issues)
    ENQUEUED = "ENQUEUED"

    # The transaction has been successful (final state)
    COMPLETED = "COMPLETED"

    # The transaction request has been submitted to the MMO and is being processed
    SUBMITTED = "SUBMITTED"

    # The transaction has failed (final state)
    FAILED = "FAILED"

    # The transaction request has been rejected
    REJECTED = "REJECTED"

    # The transaction request has been ignored as a duplicate of an already accepted transaction
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"


class Currency(Enum):
    """Supported currencies"""
    GHS = "GHS"  # Ghana Cedis
    KES = "KES"  # Kenya Shillings
    UGX = "UGX"  # Uganda Shillings
    TZS = "TZS"  # Tanzania Shillings
    RWF = "RWF"  # Rwanda Francs
    XOF = "XOF"  # West African CFA Franc
    XAF = "XAF"  # Central African CFA Franc
    ZMW = "ZMW"  # Zambian Kwacha
    MWK = "MWK"  # Malawian Kwacha
    NGN = "NGN"  # Nigerian Naira


@dataclass
class Payer:
    """Payer information for deposits"""
    type: str  # "MSISDN"
    address: Dict[str, str]  # Address object with value (which is phone number/msisdn)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "address": self.address
        }


@dataclass
class Recipient:
    """Recipient information for payouts"""
    type: str  # "MSISDN"
    value: str  # Phone number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "address": {
                "value": self.value
            }
        }


@dataclass
class DepositRequest:
    """Deposit request model"""
    deposit_id: str
    amount: str
    currency: str
    correspondent: str
    payer: Payer
    customer_timestamp: str
    statement_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "depositId": self.deposit_id,
            "amount": self.amount,
            "currency": self.currency,
            "correspondent": self.correspondent,
            "payer": self.payer.to_dict(),
            "customerTimestamp": self.customer_timestamp
        }
        if self.statement_description:
            data["statementDescription"] = self.statement_description
        return data


@dataclass
class PayoutRequest:
    """Payout request model"""
    payout_id: str
    amount: str
    country: str
    currency: str
    correspondent: str
    recipient: Recipient
    customer_timestamp: str
    statement_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "payoutId": self.payout_id,
            "amount": self.amount,
            "country": self.country,
            "currency": self.currency,
            "correspondent": self.correspondent,
            "recipient": self.recipient.to_dict(),
            "customerTimestamp": self.customer_timestamp
        }
        if self.statement_description:
            data["statementDescription"] = self.statement_description
        return data


@dataclass
class TransactionResponse:
    """Base transaction response model"""
    transaction_id: str
    status: TransactionStatus
    amount: str
    currency: str
    correspondent: str
    created: datetime
    failure_reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionResponse':
        return cls(
            transaction_id=data.get("depositId") or data.get("payoutId"),
            status=TransactionStatus(data["status"]),
            amount=data.get("amount", data.get("depositedAmount")),
            currency=data["currency"],
            correspondent=data["correspondent"],
            created=datetime.fromisoformat(data["created"].replace('Z', '+00:00')),
            failure_reason=data.get("failureReason", None)
        )


@dataclass
class DepositResponse(TransactionResponse):
    """Deposit response model"""
    deposit_id: str = ""
    payer: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DepositResponse':
        base = TransactionResponse.from_dict(data)
        return cls(
            transaction_id=base.transaction_id,
            status=base.status,
            amount=base.amount,
            currency=base.currency,
            correspondent=base.correspondent,
            created=base.created,
            failure_reason=base.failure_reason,
            deposit_id=data["depositId"],
            payer=data.get("payer", {})
        )


@dataclass
class PayoutResponse(TransactionResponse):
    """Payout response model"""
    payout_id: str = ""
    recipient: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PayoutResponse':
        base = TransactionResponse.from_dict(data)
        return cls(
            transaction_id=base.transaction_id,
            status=base.status,
            amount=base.amount,
            currency=base.currency,
            correspondent=base.correspondent,
            created=base.created,
            failure_reason=base.failure_reason,
            payout_id=data["payoutId"],
            recipient=data.get("recipient", {})
        )


@dataclass
class Correspondent:
    """Correspondent (MMO) information"""
    correspondent: str
    country: str
    currency: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Correspondent':
        return cls(
            correspondent=data["correspondent"],
            country=data["country"],
            currency=data["currency"]
        )


@dataclass
class PawaPayError:
    """Error response model"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PawaPayError':
        return cls(
            error_code=data.get("errorCode", "UNKNOWN"),
            error_message=data.get("errorMessage", "Unknown error"),
            details=data.get("details")
        )
