# PawaPay Python SDK

<img width="1536" height="1051" alt="Image" src="https://github.com/user-attachments/assets/67c81cf0-9898-4fb2-9135-30d1e4e5f90b" />

A comprehensive Python SDK for integrating with the PawaPay mobile money payment platform across Africa.

## Features

- **Deposits**: Request payments from customers
- **Payouts**: Send payments to recipients
- **Payment Pages**: Create hosted payment pages
- **Webhook Support**: Handle real-time payment notifications
- **Correspondent Prediction**: Automatically detect mobile money operators
- **Comprehensive Validation**: Built-in validation for phone numbers, amounts, and currencies
- **Error Handling**: Detailed error handling and exceptions
- **Async Support**: Built for asynchronous operations with proper polling
- **Type Safety**: Full type hints and data classes

## Supported Countries & Currencies

- 🇬🇭 Ghana (GHS)
- 🇰🇪 Kenya (KES)
- 🇺🇬 Uganda (UGX)
- 🇹🇿 Tanzania (TZS)
- 🇷🇼 Rwanda (RWF)
- 🇨🇮 Ivory Coast (XOF)
- 🇨🇲 Cameroon (XAF)
- 🇿🇲 Zambia (ZMW)
- 🇲🇼 Malawi (MWK)

## Installation

```bash
pip install pawapay-python
```

## Quick Start

### 1. Environment Setup

Create a `.env` file:

```env
PAWAPAY_API_TOKEN=your_api_token_here
PAWAPAY_ENVIRONMENT=sandbox
PAWAPAY_CALLBACK_URL=https://your-app.com/webhooks/pawapay
PAWAPAY_CALLBACK_SECRET=your_webhook_secret
```

### 2. Basic Usage

```python
from pawapay import create_client
from pawapay.exceptions import PawaPayException

# Create client from environment variables
client = create_client()

# Request a deposit (customer pays you)
try:
    deposit = client.request_deposit(
        amount="100.00",
        currency="KES",
        phone_number="254700000001",
        statement_description="Payment for order #123"
    )
    print(f"Deposit ID: {deposit.deposit_id}")
    print(f"Status: {deposit.status.value}")
except PawaPayException as e:
    print(f"Error: {e}")
```

### 3. Advanced Usage

```python
from pawapay import PawaPayClient, PawaPayConfig
from pawapay.models import TransactionStatus
from pawapay.utils import PawaPayValidator, PawaPayHelper

# Manual configuration
config = PawaPayConfig(
    api_token="your_token",
    base_url="https://api.sandbox.pawapay.co.uk",
    environment="sandbox",
    callback_url="https://your-app.com/webhooks/pawapay",
    timeout=30
)

with PawaPayClient(config) as client:
    # Get available correspondents
    correspondents = client.get_correspondents()

    # Predict correspondent for phone number
    correspondent = client.predict_correspondent("254700000001")

    # Request payout (you pay someone)
    payout = client.request_payout(
        amount="50.00",
        currency="KES",
        phone_number="254700000001",
        statement_description="Refund for order #123"
    )

    # Check status
    status = client.check_payout_status(payout.payout_id)
    if status.status == TransactionStatus.COMPLETED:
        print("Payout completed!")
```

## API Reference

### Client Methods

#### Deposits
- `request_deposit(amount, currency, phone_number, correspondent=None, statement_description=None)`
- `check_deposit_status(deposit_id)`
- `refund_deposit(deposit_id)`

#### Payouts
- `request_payout(amount, currency, phone_number, correspondent=None, statement_description=None)`
- `check_payout_status(payout_id)`

#### Configuration
- `get_active_configuration()`
- `get_correspondents()`
- `predict_correspondent(msisdn)`

#### Payment Pages
- `create_payment_page_deposit(amount, currency, return_url, statement_description=None)`

#### Utilities
- `validate_callback(payload, signature)`
- `resend_callback(transaction_id, transaction_type)`

### Webhook Handling

```python
from flask import Flask, request
from pawapay import create_client
from pawapay.utils import PawaPayHelper

app = Flask(__name__)
client = create_client()

@app.route('/webhooks/pawapay', methods=['POST'])
def handle_webhook():
    # Get signature from headers
    signature = request.headers.get('X-Signature')
    payload = request.get_data(as_text=True)

    # Validate signature
    if not client.validate_callback(payload, signature):
        return {"error": "Invalid signature"}, 401

    # Parse callback data
    callback_data = PawaPayHelper.parse_callback_payload(payload)

    # Handle the callback
    if 'depositId' in callback_data:
        # Handle deposit status change
        handle_deposit_callback(callback_data)
    elif 'payoutId' in callback_data:
        # Handle payout status change
        handle_payout_callback(callback_data)

    return {"status": "success"}, 200
```

### Error Handling

```python
from pawapay.exceptions import (
    PawaPayException,
    PawaPayAPIException,
    PawaPayValidationException
)

try:
    deposit = client.request_deposit(amount="100", currency="KES", phone_number="254700000001")
except PawaPayAPIException as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.error_code}")
except PawaPayValidationException as e:
    print(f"Validation Error: {e}")
except PawaPayException as e:
    print(f"General Error: {e}")
```

### Validation Utilities

```python
from pawapay.utils import PawaPayValidator, PawaPayHelper

# Validate phone number
if PawaPayValidator.validate_msisdn("254700000001"):
    print("Valid phone number")

# Validate amount
if PawaPayValidator.validate_amount("100.50"):
    print("Valid amount")

# Normalize phone number
normalized = PawaPayValidator.normalize_msisdn("+254 700 000 001")
# Returns: "254700000001"

# Format currency
formatted = PawaPayHelper.format_currency("100.50", "KES")
# Returns: "KSh 100.50"

# Get country from phone number
country = PawaPayHelper.get_country_from_msisdn("254700000001")
# Returns: "Kenya"
```

## Testing

### Sandbox Environment

The SDK includes test phone numbers for sandbox testing:

```python
from pawapay.utils import PawaPayHelper

test_numbers = PawaPayHelper.get_test_phone_numbers()

# Success scenarios
success_kenya = test_numbers['success']['kenya']  # "254700000001"
success_ghana = test_numbers['success']['ghana']  # "233540000001"

# Failure scenarios
failure_kenya = test_numbers['failure']['kenya']  # "254700000002"
failure_ghana = test_numbers['failure']['ghana']  # "233540000002"
```

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=pawapay
```

## Configuration Options

All configuration options can be set via environment variables or passed directly:

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `api_token` | `PAWAPAY_API_TOKEN` | - | Your PawaPay API token |
| `environment` | `PAWAPAY_ENVIRONMENT` | `sandbox` | Environment (sandbox/production) |
| `callback_url` | `PAWAPAY_CALLBACK_URL` | - | Webhook callback URL |
| `callback_secret` | `PAWAPAY_CALLBACK_SECRET` | - | Webhook signature secret |
| `enable_signed_requests` | `PAWAPAY_ENABLE_SIGNED_REQUESTS` | `false` | Enable request signing |
| `timeout` | `PAWAPAY_TIMEOUT` | `30` | Request timeout in seconds |
| `max_retries` | `PAWAPAY_MAX_RETRIES` | `3` | Maximum retry attempts |

## Project Structure

```
pawapay/
├── __init__.py          # Package initialization
├── client.py            # Main client class
├── config.py            # Configuration management
├── models.py            # Data models and enums
├── exceptions.py        # Custom exceptions
├── utils.py             # Validation and helper utilities
└── example.py           # Usage examples
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📧 Email: abimbolaronald@gmail.com
- 📖 Documentation: https://docs.pawapay.co.uk
- 🐛 Issues: https://github.com/Ronnie5562/pawapay_python_sdk/issues

## Changelog

### v1.0.0
- Initial release
- Support for deposits and payouts
- Webhook handling
- Comprehensive validation
- Full type hints and documentation

**Disclaimer:** This SDK is unofficial and not affiliated with or endorsed by PawaPay. Built for developers integrating with PawaPay’s public APIs.
