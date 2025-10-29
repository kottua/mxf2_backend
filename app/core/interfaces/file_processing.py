from abc import ABC, abstractmethod

import pandas as pd


class FileProcessingInterface(ABC):
    """
    Interface for file processing operations.
    This interface defines the contract for infrastructure layer implementations.
    """

    @abstractmethod
    async def read_excel_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Read Excel file content and return pandas DataFrame.

        Args:
            file_content: Raw file content as bytes
            filename: Name of the file for format validation

        Returns:
            pandas DataFrame with file content

        Raises:
            Exception: If file cannot be read
        """
        raise NotImplementedError

    @abstractmethod
    def validate_file_format(self, filename: str) -> None:
        """
        Validate that the file is in correct format.

        Args:
            filename: Name of the file to validate

        Raises:
            Exception: If file format is invalid
        """
        raise NotImplementedError

    @abstractmethod
    async def write_excel_file(self, df: pd.DataFrame) -> bytes:
        """
        Write pandas DataFrame to Excel file and return as bytes.

        Args:
            df: DataFrame to write

        Returns:
            Excel file content as bytes
        """
        raise NotImplementedError
