import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class PawaPayConfig:
    """Configuration class for PawaPay integration"""

    # API Configuration
    api_token: str
    base_url: str
    environment: str = "sandbox"  # sandbox or production

    # Callback Configuration
    callback_url: Optional[str] = None
    callback_secret: Optional[str] = None

    # Security Configuration
    enable_signed_requests: bool = False
    private_key_path: Optional[str] = None
    public_key_path: Optional[str] = None

    # Request Configuration
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> 'PawaPayConfig':
        """Create configuration from environment variables"""
        environment = os.getenv('PAWAPAY_ENVIRONMENT', 'sandbox')

        # Base URLs
        base_urls = {
            'sandbox': 'https://api.sandbox.pawapay.io',
            'production': 'https://api.pawapay.io'
        }

        return cls(
            api_token=os.getenv('PAWAPAY_API_TOKEN', ''),
            base_url=base_urls.get(environment, base_urls['sandbox']),
            environment=environment,
            callback_url=os.getenv('PAWAPAY_CALLBACK_URL'),
            callback_secret=os.getenv('PAWAPAY_CALLBACK_SECRET'),
            enable_signed_requests=os.getenv(
                'PAWAPAY_ENABLE_SIGNED_REQUESTS', 'false'
            ).lower() == 'true',
            private_key_path=os.getenv('PAWAPAY_PRIVATE_KEY_PATH'),
            public_key_path=os.getenv('PAWAPAY_PUBLIC_KEY_PATH'),
            timeout=int(os.getenv('PAWAPAY_TIMEOUT', '30')),
            max_retries=int(os.getenv('PAWAPAY_MAX_RETRIES', '3'))
        )

    def validate(self) -> None:
        """Validate configuration"""
        if not self.api_token:
            raise ValueError("API token is required")

        if self.enable_signed_requests and not self.private_key_path:
            raise ValueError(
                "Private key path is required when signed requests are enabled")

        if self.environment not in ['sandbox', 'production']:
            raise ValueError("Environment must be 'sandbox' or 'production'")
