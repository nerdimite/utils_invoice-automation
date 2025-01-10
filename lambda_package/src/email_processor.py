import email
import imaplib
import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
from dateutil.relativedelta import relativedelta

subject_template = "Bhavesh's Invoice #{invoice_number} dated {invoice_date}"
body_template = """
Hi,

Please find the attached my invoice for the month of {previous_month}.

Invoice number: {invoice_number}
Invoice date: {invoice_date}
Invoice amount: {invoice_amount}


Thanks,
Bhavesh
"""


class EmailProcessor:
    """
    A class to process emails, including connecting to an IMAP server,
    scanning for unread emails, and sending emails with PDF attachments.

    Attributes:
        email_address (str): The email address used for sending and receiving emails.
        email_password (str): The password for the email account.
        approved_senders (list): A list of approved sender email addresses.
        imap_server (str): The IMAP server address (default is Gmail).
        smtp_server (str): The SMTP server address (default is Gmail).
        smtp_port (int): The port for the SMTP server (default is 587).
        scan_start_time (datetime): The time when the email scanning starts.
    """

    def __init__(
        self,
        email_address: str,
        email_password: str,
        approved_senders: list,
        imap_server: str = "imap.gmail.com",
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        """
        Initializes the EmailProcessor with the provided email credentials and settings.

        Args:
            email_address (str): The email address for the account.
            email_password (str): The password for the email account.
            approved_senders (list): A list of approved sender email addresses.
            imap_server (str): The IMAP server address (default is Gmail).
            smtp_server (str): The SMTP server address (default is Gmail).
            smtp_port (int): The port for the SMTP server (default is 587).
        """
        self.email_address = email_address
        self.email_password = email_password
        self.approved_senders = [email.lower() for email in approved_senders]
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.scan_start_time = datetime.now(pytz.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    def connect_imap(self):
        """
        Connects to the IMAP server and logs in with the provided credentials.

        Returns:
            imaplib.IMAP4_SSL: The connected IMAP instance.
        """
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.email_address, self.email_password)
        return imap

    def scan_emails(self):
        """
        Scans the inbox for unread emails from approved senders that were received
        after the scan start time. Returns the details of the first matching email.

        Returns:
            list: A list of dictionaries containing the sender's email, the date of the email,
                  and the body text of the email, or an empty list if no matching email is found.
        """
        imap = self.connect_imap()
        imap.select("INBOX")

        # Search for unread emails received after scan start time
        date_str = self.scan_start_time.strftime("%d-%b-%Y")
        search_criteria = f'(UNSEEN SINCE "{date_str}")'
        _, message_numbers = imap.search(None, search_criteria)

        matching_emails = []

        for num in message_numbers[0].split():
            _, msg_data = imap.fetch(num, "(RFC822)")
            email_body = email.message_from_bytes(msg_data[0][1])

            # Get sender's email
            from_email = email.utils.parseaddr(email_body["From"])[1].lower()

            # Skip if sender is not in approved list
            if from_email not in self.approved_senders:
                print(f"Skipping email from non-approved sender: {from_email}")
                continue

            # Get email subject
            email_subject = email_body["Subject"]

            # Get email date and make it timezone-aware
            email_date_str = email_body["Date"]
            email_date = email.utils.parsedate_to_datetime(email_date_str)
            if email_date.tzinfo is None:
                email_date = pytz.UTC.localize(email_date)

            # Skip if email is older than scan start time
            if email_date < self.scan_start_time:
                continue

            # Format email date for invoice (convert to IST for display)
            ist = pytz.timezone("Asia/Kolkata")
            email_date_str = email_date.astimezone(ist).strftime("%d %B %Y")

            # Extract text content
            text_content = ""
            if email_body.is_multipart():
                for part in email_body.walk():
                    if part.get_content_type() == "text/plain":
                        text_content += part.get_payload(decode=True).decode()
            else:
                text_content = email_body.get_payload(decode=True).decode()

            matching_emails.append(
                {
                    "from_email": from_email,
                    "date": email_date_str,
                    "subject": email_subject,
                    "body_text": text_content,
                }
            )

        return matching_emails

    def send_email_with_pdf(
        self, to_email: str, subject: str, body: str, pdf_path: str
    ) -> None:
        """
        Sends an email with a PDF attachment.

        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body text of the email.
            pdf_path (str): The file path of the PDF to attach.
        """
        msg = MIMEMultipart()
        msg["From"] = self.email_address
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if pdf_path:
            with open(pdf_path, "rb") as f:
                pdf = MIMEApplication(f.read(), _subtype="pdf")
                pdf.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(pdf_path),
                )
                msg.attach(pdf)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)

    def send_invoice_email(self, invoice_pdf_path: str, invoice_params: dict) -> None:
        """
        Sends the email with the invoice PDF attachment.

        Args:
            invoice_pdf_path (str): The file path of the invoice PDF to attach.
            invoice_params (dict): A dictionary containing the invoice parameters.

            invoice_params contains:
                - invoice_number (int): The invoice number.
                - amount (float): The invoice amount.
                - email_params (dict): A dictionary containing the email parameters.
                    - from_email (str): The email address of the sender.
                    - date (str): The date of the invoice.
                    - subject (str): The subject of the original email.
                    - body_text (str): The body text of the original email.

        Returns:
            None
        """
        current_date = datetime.strptime(
            invoice_params["email_params"]["date"], "%d %B %Y"
        )
        previous_month = (current_date - relativedelta(months=1)).strftime("%B")

        subject = subject_template.format(
            invoice_number=invoice_params["invoice_number"],
            invoice_date=invoice_params["email_params"]["date"],
        )
        body = body_template.format(
            invoice_number=invoice_params["invoice_number"],
            invoice_date=invoice_params["email_params"]["date"],
            invoice_amount=invoice_params["amount"],
            previous_month=previous_month,
        )

        self.send_email_with_pdf(
            to_email=invoice_params["email_params"]["from_email"],
            subject=subject,
            body=body,
            pdf_path=invoice_pdf_path,
        )
