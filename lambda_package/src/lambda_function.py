import json
import os

from email_processor import EmailProcessor
from extraction_utils import InvoiceParamExtractor
from invoice_generator import InvoiceGenerator
from s3_utils import S3Utils

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

APPROVED_SENDERS = [email.strip() for email in os.getenv("APPROVED_SENDERS").split(",")]

email_processor = EmailProcessor(EMAIL, PASSWORD, APPROVED_SENDERS)
s3_utils = S3Utils()
invoice_param_extractor = InvoiceParamExtractor()
invoice_generator = InvoiceGenerator()


def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Scan emails as per search criteria of approved senders today
    scanned_emails = email_processor.scan_emails()
    print(f"Scanned emails: {json.dumps(scanned_emails, indent=2)}")

    # Get the next invoice number
    next_invoice_number = s3_utils.get_last_invoice_number() + 1

    # Extract invoice params from emails
    invoice_params_list = []
    for result in scanned_emails:
        invoice_params = invoice_param_extractor.extract_invoice_params(
            json.dumps(result, indent=2)
        )
        print(invoice_params)
        if invoice_params.is_invoice:
            invoice_params_list.append(
                {
                    "invoice_number": next_invoice_number,
                    "amount": invoice_params.invoice_amount,
                    "email_params": result,
                }
            )
            next_invoice_number += 1

    print(f"Invoice parameters list: {json.dumps(invoice_params_list, indent=2)}")

    # Generate invoices
    output_invoice_paths = []
    for invoice_params in invoice_params_list:
        invoice_path = invoice_generator.generate_invoice(
            invoice_number=invoice_params["invoice_number"],
            date=invoice_params["email_params"]["date"],
            amount=invoice_params["amount"],
        )
        output_invoice_paths.append(invoice_path)

    print(f"Output invoice paths: {output_invoice_paths}")

    # Send invoices to recipients
    for invoice_path, invoice_params in zip(output_invoice_paths, invoice_params_list):
        email_processor.send_invoice_email(invoice_path, invoice_params)
        filename = invoice_path.split("/tmp/")[-1]
        print(
            f"Sent invoice {filename} to {invoice_params['email_params']['from_email']}"
        )
        try:
            s3_utils.upload_file(invoice_path, f"cellstrat_invoices/{filename}")
            print(f"Uploaded invoice {filename} to S3")
        except Exception as e:
            print(f"Error uploading invoice {filename} to S3: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f"Successfully processed {len(invoice_params_list)} invoices"}
        ),
    }
