import os
from locale import LC_ALL, setlocale

import pdfkit
from jinja2 import Environment, FileSystemLoader
from num2words import num2words

# Set locale for number formatting
setlocale(LC_ALL, "")


class InvoiceGenerator:
    """
    A class to generate invoices in PDF format using Jinja2 templates.

    Attributes:
        template_path (str): The file path to the Jinja2 template for the invoice.
    """

    def __init__(self, template_path: str = "invoice_template.html"):
        """
        Initializes the InvoiceGenerator with the specified template path.

        Args:
            template_path (str): The file path to the Jinja2 template for the invoice.
        """
        self.template_path = template_path

    @staticmethod
    def format_amount(amount):
        """
        Formats the given amount with commas for Indian number formatting.

        Args:
            amount (float): The amount to format.

        Returns:
            str: The formatted amount as a string.
        """
        return f"{amount:,}"

    @staticmethod
    def amount_to_words(amount):
        """
        Converts the given amount to words in Indian English.

        Args:
            amount (float): The amount to convert.

        Returns:
            str: The amount in words.
        """
        return num2words(amount, lang="en_IN").title()

    def generate_invoice(self, invoice_number, date, amount):
        """
        Generates an invoice PDF file using the specified invoice number, date, and amount.

        Args:
            invoice_number (str): The invoice number.
            date (str): The date of the invoice.
            amount (float): The amount to be included in the invoice.

        Returns:
            str: The file path of the generated PDF invoice.
        """
        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(self.template_path)

        # Prepare template variables
        amount_formatted = self.format_amount(amount)
        amount_words = self.amount_to_words(amount)

        # Render template
        html_content = template.render(
            invoice_number=invoice_number,
            date=date,
            amount_formatted=amount_formatted,
            amount_words=amount_words,
        )

        # Save HTML to temporary file
        with open("/tmp/temp.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert HTML to PDF
        output_filename = f"/tmp/Bhavesh Invoice {invoice_number:03d}.pdf"
        pdfkit.from_file("/tmp/temp.html", output_filename)

        # Clean up temporary file
        os.remove("/tmp/temp.html")

        return output_filename
