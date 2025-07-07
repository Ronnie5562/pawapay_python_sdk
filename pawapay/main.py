"""
Example usage of PawaPay Python SDK
"""

import os
import time
from datetime import datetime
from .models import TransactionStatus
from .utils import PawaPayValidator, PawaPayHelper
from . import PawaPayClient, PawaPayConfig, create_client
from .exceptions import PawaPayException, PawaPayAPIException


def main():
    """Main example function"""

    # Method 1: Create client from environment variables
    # Make sure to set your environment variables first
    try:
        client = create_client()
        print("Created client from environment variables")
    except Exception as e:
        print(f"Failed to create client from environment: {e}")

        # Method 2: Create client with manual configuration
        config = PawaPayConfig(
            api_token="your_api_token_here",
            base_url="https://api.sandbox.pawapay.co.uk",
            environment="sandbox",
            callback_url="https://your-app.com/webhooks/pawapay",
            timeout=30
        )
        client = PawaPayClient(config)
        print("Created client with manual configuration")

    # Example 1: Get available correspondents
    print("\n=== Getting Available Correspondents ===")
    try:
        correspondents = client.get_correspondents()
        print(f"Found {len(correspondents)} correspondents:")
        for correspondent in correspondents[:5]:  # Show first 5
            print(f"  - {correspondent.correspondent} ({correspondent.country}) - {correspondent.currency}")
    except PawaPayException as e:
        print(f"✗ Error getting correspondents: {e}")

    # Example 2: Predict correspondent for a phone number
    print("\n=== Predicting Correspondent ===")
    test_phone = "254700000001"  # Kenya test number
    try:
        correspondent = client.predict_correspondent(test_phone)
        print(f"Predicted correspondent for {test_phone}: {correspondent}")
    except PawaPayException as e:
        print(f"✗ Error predicting correspondent: {e}")

    # Example 3: Request a deposit (customer pays you)
    print("\n=== Requesting Deposit ===")
    try:
        # Validate inputs first
        amount = "100.00"
        currency = "KES"
        phone_number = "254700000001"  # Kenya test number for success

        if not PawaPayValidator.validate_amount(amount):
            print("✗ Invalid amount format")
            return

        if not PawaPayValidator.validate_msisdn(phone_number):
            print("✗ Invalid phone number format")
            return

        # Request deposit
        deposit_response = client.request_deposit(
            amount=amount,
            currency=currency,
            phone_number=phone_number,
            statement_description="Test deposit"
        )

        print(f"  Deposit requested successfully!")
        print(f"  Deposit ID: {deposit_response.deposit_id}")
        print(f"  Status: {deposit_response.status.value}")
        print(f"  Amount: {PawaPayHelper.format_currency(deposit_response.amount, deposit_response.currency)}")
        print(f"  Created: {deposit_response.created}")

        # Check deposit status
        print(f"\n--- Checking Deposit Status ---")
        deposit_status = client.check_deposit_status(deposit_response.deposit_id)
        print(f"Current Status: {deposit_status.status.value}")

        if deposit_status.status == TransactionStatus.FAILED:
            print(f"Failure Reason: {deposit_status.failure_reason}")

    except PawaPayAPIException as e:
        print(f"  API Error requesting deposit: {e}")
        print(f"  Status Code: {e.status_code}")
        print(f"  Error Code: {e.error_code}")
    except PawaPayException as e:
        print(f"  Error requesting deposit: {e}")

    # Example 4: Request a payout (you pay someone)
    print("\n=== Requesting Payout ===")
    try:
        payout_response = client.request_payout(
            amount="50.00",
            currency="KES",
            phone_number="254700000001",  # Kenya test number
            statement_description="Test payout"
        )

        print(f"  Payout requested successfully!")
        print(f"  Payout ID: {payout_response.payout_id}")
        print(f"  Status: {payout_response.status.value}")
        print(f"  Amount: {PawaPayHelper.format_currency(payout_response.amount, payout_response.currency)}")

        # Check payout status
        print(f"\n--- Checking Payout Status ---")
        payout_status = client.check_payout_status(payout_response.payout_id)
        print(f"Current Status: {payout_status.status.value}")

    except PawaPayAPIException as e:
        print(f"  API Error requesting payout: {e}")
    except PawaPayException as e:
        print(f"  Error requesting payout: {e}")

    # Example 5: Create payment page deposit
    print("\n=== Creating Payment Page Deposit ===")
    try:
        payment_page_response = client.create_payment_page_deposit(
            amount="25.00",
            currency="KES",
            return_url="https://your-app.com/payment-success",
            statement_description="Payment page test"
        )

        print(f"  Payment page created successfully!")
        print(f"  Payment URL: {payment_page_response.get('paymentUrl')}")
        print(f"  Deposit ID: {payment_page_response.get('depositId')}")

    except PawaPayException as e:
        print(f"  Error creating payment page: {e}")

    # Example 6: Utility functions
    print("\n=== Utility Functions ===")

    # Test phone numbers
    test_numbers = PawaPayHelper.get_test_phone_numbers()
    print("Test phone numbers:")
    print(f"  Success (Ghana): {test_numbers['success']['ghana']}")
    print(f"  Failure (Kenya): {test_numbers['failure']['kenya']}")

    # Country detection
    country = PawaPayHelper.get_country_from_msisdn("254700000001")
    print(f"Country for 254700000001: {country}")

    # Currency formatting
    formatted = PawaPayHelper.format_currency("100.50", "KES")
    print(f"Formatted currency: {formatted}")

    print("\n=== Example Complete ===")

def webhook_handler_example():
    """Example webhook handler for callbacks"""
    print("\n=== Webhook Handler Example ===")

    # This would be your Flask/FastAPI/Django webhook endpoint
    def handle_pawapay_webhook(request):
        """Handle PawaPay webhook callback"""

        # Get the signature from headers
        signature = request.headers.get('X-Signature')
        payload = request.get_data(as_text=True)

        # Create client to validate signature
        client = create_client()

        try:
            # Validate signature
            if not client.validate_callback(payload, signature):
                return {"error": "Invalid signature"}, 401

            # Parse payload
            callback_data = PawaPayHelper.parse_callback_payload(payload)

            # Handle different transaction types
            if 'depositId' in callback_data:
                # Handle deposit callback
                deposit_id = callback_data['depositId']
                status = callback_data['status']

                print(f"Deposit {deposit_id} status: {status}")

                # Update your database
                # update_deposit_status(deposit_id, status)

            elif 'payoutId' in callback_data:
                # Handle payout callback
                payout_id = callback_data['payoutId']
                status = callback_data['status']

                print(f"Payout {payout_id} status: {status}")

                # Update your database
                # update_payout_status(payout_id, status)

            return {"status": "success"}, 200

        except Exception as e:
            print(f"Error processing webhook: {e}")
            return {"error": "Processing failed"}, 500

    print("Webhook handler example defined")
    print("Remember to:")
    print("1. Set up your webhook endpoint URL")
    print("2. Configure the URL in PawaPay dashboard")
    print("3. Set the webhook secret in your environment variables")

if __name__ == "__main__":
    main()
    webhook_handler_example()
