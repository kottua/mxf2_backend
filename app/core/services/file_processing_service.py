import pandas as pd
from app.core.exceptions.domain import DataValidationException, MissingRequiredColumnsException
from app.core.interfaces.file_processing import FileProcessingInterface
from app.core.schemas.income_plan_schemas import IncomePlanFileResponse
from app.core.schemas.premise_schemas import PremisesFileSpecificationResponse


class FileProcessingService:
    """
    Service for processing uploaded files (Excel specifications, income plans, etc.).

    This service contains all business logic for file processing, following the onion architecture pattern.
    It coordinates between the API layer and infrastructure layer while maintaining business rules.
    """

    def __init__(self, file_processor: FileProcessingInterface):
        """
        Initialize the file processing service.

        Args:
            file_processor: Implementation of FileProcessingInterface for technical file operations
        """
        self.file_processor = file_processor

    async def process_specification(
        self, file_content: bytes, filename: str
    ) -> list[PremisesFileSpecificationResponse]:
        """
        Process uploaded premises specification file.

        This method contains all business logic for processing premises specification files:
        - File format validation
        - Reading file content
        - Column validation
        - Data validation and transformation

        Args:
            file_content: Raw file content as bytes
            filename: Name of the uploaded file

        Returns:
            List of validated premises data dictionaries

        Raises:
            FileProcessingException: If file processing fails
        """
        # Step 1: Validate file format (business rule)
        self.file_processor.validate_file_format(filename)

        # Step 2: Read Excel file (technical operation)
        df = await self.file_processor.read_excel_file(file_content, filename)

        # Step 3: Validate required columns (business rule)
        self._validate_required_columns(df, PremisesFileSpecificationResponse.PREDEFINED_COLUMNS)

        # Step 4: Process and validate data (business logic)
        premises_list: list[PremisesFileSpecificationResponse] = []

        for i, row in df.iterrows():
            try:
                # Validate row data using Pydantic model (business logic)
                premises_row = PremisesFileSpecificationResponse.custom_model_validate(dict(row))
                premises_list.append(premises_row)

            except Exception as e:
                # Extract validation errors for better error reporting
                error_details = str(e)
                if hasattr(e, "errors"):
                    error_details = str(e.errors())

                raise DataValidationException(row_number=i + 2, error_details=error_details)

        return premises_list

    async def process_income_plan(self, file_content: bytes, filename: str) -> list[IncomePlanFileResponse]:
        """
        Process uploaded income plan file.

        Args:
            file_content: Raw file content as bytes
            filename: Name of the uploaded file

        Returns:
            List of validated income plan data dictionaries

        Raises:
            NotImplementedError: Method not yet implemented
        """
        # Step 1: Validate file format (business rule)
        self.file_processor.validate_file_format(filename)

        # Step 2: Read Excel file (technical operation)
        df = await self.file_processor.read_excel_file(file_content, filename)

        # Step 3: Validate required columns (business rule)
        self._validate_required_columns(df, IncomePlanFileResponse.PREDEFINED_COLUMNS)

        income_plans: list[IncomePlanFileResponse] = []
        for i, row in df.iterrows():
            try:
                # Validate row data using Pydantic model (business logic)
                income_plan_row = IncomePlanFileResponse.model_validate(dict(row))
                income_plans.append(income_plan_row)

            except Exception as e:
                # Extract validation errors for better error reporting
                error_details = str(e)
                if hasattr(e, "errors"):
                    error_details = str(e.errors())

                raise DataValidationException(row_number=i + 2, error_details=error_details)

        return income_plans

    def _validate_required_columns(self, df: pd.DataFrame, predefined_columns: list[str]) -> None:
        """
        Validate that all required columns are present in the DataFrame.

        This is a business rule that defines which columns must be present
        in premises specification files.

        Args:
            df: DataFrame to validate

        Raises:
            MissingRequiredColumnsException: If required columns are missing
        """
        # Clean column names (remove extra whitespace)
        df.columns = df.columns.str.strip()

        # Check for missing required columns
        missing_columns = [col for col in predefined_columns if col.strip() not in df.columns]

        if missing_columns:
            raise MissingRequiredColumnsException(missing_columns)
