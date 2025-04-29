from typing import Callable, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()


class InvoiceParams(BaseModel):
    is_invoice: bool = Field(
        description="Whether the email body is asking for an invoice"
    )
    invoice_amount: Optional[int] = Field(description="The amount in the invoice")
    invoice_date: Optional[str] = Field(
        description="The date for the invoice in format '%d %B %Y' like '30 April 2025'"
    )


def openai_structured_chat_completion(
    messages: list[dict],
    response_format: BaseModel,
    model: str = "gpt-4o-mini",
    **kwargs
) -> BaseModel:
    """
    OpenAI structured chat completion.

    Args:
        messages: List of messages to send to the model.
        response_format: Pydantic model to parse the response into.
        **kwargs: Additional keyword arguments to pass to the OpenAI API.
    """
    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=response_format,
        **kwargs,
    )
    return completion.choices[0].message.parsed


class InvoiceParamExtractor:
    """
    A class to extract invoice parameters from email body text using an LLM provider.

    This class uses a language model to analyze email content and determine if it contains
    an invoice request, along with extracting relevant invoice details like date and amount.

    Attributes:
        llm_provider_function (Callable): Function that provides LLM capabilities, defaults to openai_structured_chat_completion
        system_prompt (str): The prompt that guides the LLM in extracting invoice parameters
    """

    def __init__(
        self, llm_provider_function: Callable = openai_structured_chat_completion
    ):
        """
        Initialize the InvoiceParamExtractor.

        Args:
            llm_provider_function (Callable, optional): Function that provides LLM capabilities.
                Defaults to openai_structured_chat_completion.
        """
        self.llm_provider_function = llm_provider_function
        self.system_prompt = """You will be given an email body. First check if the email body is asking for an invoice with some defined amount. If it is, extract the invoice amount and the invoice date (if mentioned explicitly in the body). If it is not, return None for the amount and date can be the email date."""

    def extract_invoice_params(self, email_body: str) -> InvoiceParams:
        """
        Extract invoice parameters from the given email body.

        Uses the configured LLM provider to analyze the email content and extract
        invoice-related information.

        Args:
            email_body (str): The email body text to analyze

        Returns:
            InvoiceParams: A Pydantic model containing:
                - is_invoice (bool): Whether the email is requesting an invoice
                - invoice_amount (Optional[int]): The invoice amount if present
                - invoice_date (Optional[date]): The date for the invoice if present
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": email_body},
        ]
        return self.llm_provider_function(messages, InvoiceParams)
