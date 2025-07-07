from typing import Optional, Dict, Any

class PawaPayException(Exception):
    """Base exception for PawaPay SDK"""
    pass

class PawaPayAPIException(PawaPayException):
    """Exception for API-specific errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

    def __str__(self):
        parts = [super().__str__()]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        return " | ".join(parts)

class PawaPayValidationException(PawaPayException):
    """Exception for validation errors"""
    pass

class PawaPayConfigurationException(PawaPayException):
    """Exception for configuration errors"""
    pass

class PawaPayTimeoutException(PawaPayException):
    """Exception for timeout errors"""
    pass

class PawaPayNetworkException(PawaPayException):
    """Exception for network-related errors"""
    pass
