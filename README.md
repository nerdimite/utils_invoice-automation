# CellStrat Invoice Automation

An automated invoice generation and processing system that monitors emails, generates invoices, and sends them to recipients. The system is deployed as an AWS Lambda function.

## System Requirements

- Python 3.8+
- wkhtmltopdf (for PDF generation)
- AWS account with appropriate permissions
- Docker (for local testing and deployment)

## Setup Instructions

1. Install system dependencies:

   ```bash
   sudo apt-get install wkhtmltopdf
   ```

2. Install Python dependencies:

   ```bash
   pip install -r lambda_package/requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file with the following variables:

   ```
   OPENAI_API_KEY=your_openai_api_key
   EMAIL=your_email@example.com
   PASSWORD=your_email_password
   APPROVED_SENDERS=sender1@example.com,sender2@example.com
   ```

   Gmail Password is actually the app password. See [Google App Passwords](https://support.google.com/accounts/answer/185833) for setup instructions.

4. Build and deploy the Lambda function:
   ```bash
   cd lambda_package
   ./build_deploy.sh
   ```

## Project Structure

### Lambda Package Directory (`lambda_package/`)

- `requirements.txt`: Python dependencies required for the project
- `build_deploy.sh`: Script for building and deploying the Lambda function
- `Dockerfile`: Container configuration for Lambda deployment

### Source Code (`lambda_package/src/`)

- `lambda_function.py`: Main entry point for the AWS Lambda function. Orchestrates the entire invoice processing workflow.
- `email_processor.py`: Handles email scanning and sending functionality.
- `extraction_utils.py`: Contains utilities for extracting invoice parameters from email content.
- `invoice_generator.py`: Generates PDF invoices using the HTML template.
- `s3_utils.py`: Manages AWS S3 operations for storing invoices and tracking invoice numbers.
- `invoice_template.html`: HTML template for generating invoices.
- `email_template.py`: Template for outgoing emails with invoices.

## Workflow

1. The Lambda function is triggered (can be scheduled or event-driven)
2. Scans emails from approved senders
3. Extracts invoice parameters from email content
4. Generates PDF invoices using the template
5. Sends invoices back to the original senders
6. Stores invoices in S3 for record-keeping
