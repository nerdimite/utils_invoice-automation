import re
from typing import List, Optional

import boto3


class S3Utils:
    """
    Utility class for AWS S3 operations related to invoice files.
    """

    def __init__(self, bucket_name: str = "project-ava"):
        """
        Initialize S3Utils with bucket name.

        Args:
            bucket_name (str): Name of the S3 bucket
        """
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name

    def list_invoice_files(
        self, prefix: str = "cellstrat_invoices/Bhavesh Invoice ", page_size: int = 1000
    ) -> List[str]:
        """
        Lists all invoice PDF files in the bucket matching the pattern "Bhavesh Invoice XXX.pdf"
        with pagination support.

        Args:
            prefix (str): Prefix to filter files (default: "Bhavesh Invoice ")
            page_size (int): Number of items per page (default: 1000)

        Returns:
            List[str]: List of matching S3 keys/paths
        """
        invoice_files = []
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix, MaxKeys=page_size
        )
        invoice_files.extend(response.get("Contents", []))

        while response.get("IsTruncated"):
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=page_size,
                ContinuationToken=response.get("NextContinuationToken"),
            )
            invoice_files.extend(response.get("Contents", []))

        invoice_files = [result["Key"] for result in invoice_files]

        # Filter and sort files, skipping any that don't match the expected pattern
        valid_files = []
        for file in invoice_files:
            try:
                # Extract the number from filename
                number = int(file.split(" ")[-1].split(".")[0])
                valid_files.append((number, file))
            except (IndexError, ValueError):
                # Skip files that don't match the expected pattern
                continue

        # Sort by the extracted number and return just the filenames
        return [file for _, file in sorted(valid_files)]

    def get_last_invoice_number(self) -> int:
        """
        Get the last invoice number.
        """
        return int(self.list_invoice_files()[-1].split(" ")[-1].split(".")[0])

    def upload_file(self, local_file_path: str, s3_key: str) -> bool:
        """
        Uploads a file to S3.

        Args:
            local_file_path (str): Path to local file
            s3_key (str): Destination key in S3

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
            return True
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return False

    def download_file(self, s3_key: str, local_file_path: str) -> bool:
        """
        Downloads a file from S3.

        Args:
            s3_key (str): Source key in S3
            local_file_path (str): Destination path for local file

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_file_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False
