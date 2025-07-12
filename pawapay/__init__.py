"""
PawaPay Python SDK

A comprehensive SDK for integrating with the PawaPay mobile money payment platform.
"""

from .config import PawaPayConfig
from .client import PawaPayClient
from .models import (
    DepositRequest,
    PayoutRequest,
    DepositResponse,
    PayoutResponse,
    Correspondent,
    PawaPayError,
    TransactionStatus,
    Payer,
    Recipient,
    Currency
)
from .exceptions import (
    PawaPayException,
    PawaPayAPIException,
    PawaPayValidationException,
    PawaPayConfigurationException,
    PawaPayTimeoutException,
    PawaPayNetworkException
)
from .utils import PawaPayValidator, PawaPayHelper
from .client import create_client
from dotenv import load_dotenv

load_dotenv()

__version__ = "1.0.0"
__author__ = "Abimbola Ronald"
__email__ = "abimbolaronald@gmail.com"

__all__ = [
    # Core classes
    'PawaPayConfig',
    'PawaPayClient',

    # Models
    'DepositRequest',
    'PayoutRequest',
    'DepositResponse',
    'PayoutResponse',
    'Correspondent',
    'PawaPayError',
    'TransactionStatus',
    'Payer',
    'Recipient',
    'Currency',

    # Exceptions
    'PawaPayException',
    'PawaPayAPIException',
    'PawaPayValidationException',
    'PawaPayConfigurationException',
    'PawaPayTimeoutException',
    'PawaPayNetworkException',

    # Utilities
    'PawaPayValidator',
    'PawaPayHelper',
]
