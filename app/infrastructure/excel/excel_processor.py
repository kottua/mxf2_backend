from io import BytesIO

import pandas as pd
from app.core.exceptions.domain import FileReadException, InvalidFileFormatException
from app.core.interfaces.file_processing import FileProcessingInterface


class ExcelProcessor(FileProcessingInterface):
    """
    Infrastructure layer implementation for Excel file processing.

    This class handles only the technical aspects of reading Excel files,
    while business logic remains in the service layer.
    """

    async def read_excel_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Read Excel file content into pandas DataFrame.

        Args:
            file_content: Raw file content as bytes
            filename: Name of the file for validation

        Returns:
            pandas DataFrame with file content

        Raises:
            FileReadException: If file cannot be read
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            return df
        except Exception as e:
            raise FileReadException(f"Failed to read Excel file '{filename}': {str(e)}")

    def validate_file_format(self, filename: str) -> None:
        """
        Validate that the file is in Excel format.

        Args:
            filename: Name of the file to validate

        Raises:
            InvalidFileFormatException: If file format is invalid
        """
        if not filename or not filename.endswith((".xlsx", ".xls")):
            raise InvalidFileFormatException(f"File '{filename}' must be in .xlsx or .xls format")
