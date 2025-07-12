import re
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation
from exceptions import PawaPayValidationException


class PawaPayValidator:
    """Validation utilities for PawaPay"""

    @staticmethod
    def validate_msisdn(msisdn: str) -> bool:
        """Validate phone number format"""
        # Remove any spaces, dashes, or plus signs
        clean_msisdn = re.sub(r'[\s\-\+]', '', msisdn)

        # Check if it's all digits and has reasonable length
        if not clean_msisdn.isdigit():
            return False

        # Most African phone numbers are 9-15 digits
        if len(clean_msisdn) < 9 or len(clean_msisdn) > 15:
            return False

        return True

    @staticmethod
    def validate_amount(amount: str) -> bool:
        """Validate amount format"""
        try:
            decimal_amount = Decimal(amount)

            # Must be positive
            if decimal_amount <= 0:
                return False

            # Check decimal places (max 2)
            if decimal_amount.as_tuple().exponent < -2:
                return False

            # Check if it's too large (arbitrary limit)
            if decimal_amount > Decimal('9999999999'):
                return False

            return True

        except (InvalidOperation, ValueError):
            return False

    @staticmethod
    def validate_currency(currency: str) -> bool:
        """Validate currency code"""
        valid_currencies = {
            'GHS', 'KES', 'UGX', 'TZS', 'RWF',
            'XOF', 'XAF', 'ZMW', 'MWK'
        }
        return currency.upper() in valid_currencies

    @staticmethod
    def normalize_msisdn(msisdn: str) -> str:
        """Normalize phone number format"""
        # Remove any spaces, dashes, or plus signs
        clean_msisdn = re.sub(r'[\s\-\+]', '', msisdn)

        if not PawaPayValidator.validate_msisdn(clean_msisdn):
            raise PawaPayValidationException(f"Invalid phone number format: {msisdn}")

        return clean_msisdn

    @staticmethod
    def normalize_amount(amount: str) -> str:
        """Normalize amount format"""
        try:
            decimal_amount = Decimal(amount)

            if not PawaPayValidator.validate_amount(amount):
                raise PawaPayValidationException(f"Invalid amount: {amount}")

            # Format to remove trailing zeros but keep at least one decimal place if needed
            normalized = str(decimal_amount.normalize())

            # Ensure we don't have scientific notation
            if 'E' in normalized.upper():
                # Convert back to regular decimal notation
                normalized = format(decimal_amount, 'f')

            return normalized

        except (InvalidOperation, ValueError):
            raise PawaPayValidationException(f"Invalid amount format: {amount}")


class PawaPayHelper:
    """Helper utilities for PawaPay"""

    @staticmethod
    def get_test_phone_numbers() -> Dict[str, Dict[str, str]]:
        """Get test phone numbers for sandbox testing"""
        return {
            "success": {
                "ghana": "233540000001",
                "kenya": "254700000001",
                "uganda": "256700000001",
                "tanzania": "255700000001",
                "rwanda": "250700000001"
            },
            "failure": {
                "ghana": "233540000002",
                "kenya": "254700000002",
                "uganda": "256700000002",
                "tanzania": "255700000002",
                "rwanda": "250700000002"
            }
        }

    @staticmethod
    def format_currency(amount: str, currency: str) -> str:
        """Format amount with currency symbol"""
        currency_symbols = {
            'GHS': '₵',
            'KES': 'KSh',
            'UGX': 'USh',
            'TZS': 'TSh',
            'RWF': 'RF',
            'XOF': 'CFA',
            'XAF': 'FCFA',
            'ZMW': 'ZK',
            'MWK': 'MK'
        }

        symbol = currency_symbols.get(currency.upper(), currency.upper())
        return f"{symbol} {amount}"

    @staticmethod
    def parse_callback_payload(payload: str) -> Dict[str, Any]:
        """Parse callback payload from JSON string"""
        import json
        try:
            return json.loads(payload)
        except json.JSONDecodeError as e:
            raise PawaPayValidationException(f"Invalid JSON payload: {str(e)}")

    @staticmethod
    def generate_statement_description(transaction_type: str, reference: str) -> str:
        """Generate statement description"""
        return f"{transaction_type.upper()} - {reference}"

    @staticmethod
    def get_country_from_msisdn(msisdn: str) -> Optional[str]:
        """Get country code from phone number"""
        country_codes = {
            '233': 'Ghana',
            '254': 'Kenya',
            '256': 'Uganda',
            '255': 'Tanzania',
            '250': 'Rwanda',
            '225': 'Ivory Coast',
            '237': 'Cameroon',
            '260': 'Zambia',
            '265': 'Malawi'
        }

        normalized = PawaPayValidator.normalize_msisdn(msisdn)

        # Check for 3-digit country codes
        for code, country in country_codes.items():
            if normalized.startswith(code):
                return country

        return None
