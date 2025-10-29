import pandas as pd
from app.core.exceptions.domain import DataValidationException, MissingRequiredColumnsException, ObjectNotFound
from app.core.interfaces.committed_prices_repository import CommittedPricesRepositoryInterface
from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.core.interfaces.file_processing import FileProcessingInterface
from app.core.interfaces.premises_repository import PremisesRepositoryInterface
from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.core.schemas.calculation_schemas import PremisesWithCalculation
from app.core.schemas.income_plan_schemas import IncomePlanFileResponse
from app.core.schemas.premise_schemas import PremisesFileSpecificationCreate, PremisesFileSpecificationResponse


class FileProcessingService:
    """
    Service for processing uploaded files (Excel specifications, income plans, etc.).

    This service contains all business logic for file processing, following the onion architecture pattern.
    It coordinates between the API layer and infrastructure layer while maintaining business rules.
    """

    def __init__(
        self,
        file_processor: FileProcessingInterface,
        distribution_repository: DistributionConfigsRepositoryInterface,
        reo_repository: RealEstateObjectRepositoryInterface,
        premises_repository: PremisesRepositoryInterface,
        committed_prices_repository: CommittedPricesRepositoryInterface,
    ):
        """
        Initialize the file processing service.

        Args:
            file_processor: Implementation of FileProcessingInterface for technical file operations
        """
        self.file_processor = file_processor
        self.distribution_repository = distribution_repository
        self.reo_repository = reo_repository
        self.premises_repository = premises_repository
        self.committed_prices_repository = committed_prices_repository

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

    async def generate_excel_with_actual_price(self, reo_id: int, distribution_config_id: int) -> bytes:
        """
        Generate Excel file with premises data and actual_price_per_sqm from committed prices.

        Args:
            reo_id: Real estate object ID
            distribution_config_id: Distribution config ID

        Returns:
            Excel file content as bytes

        Raises:
            ObjectNotFound: If premises or committed prices not found
        """
        # Get committed prices
        committed_prices = await self.committed_prices_repository.get_by_reo_and_distribution_config(
            reo_id=reo_id, distribution_config_id=distribution_config_id, is_active=True
        )
        if not committed_prices:
            raise ObjectNotFound(
                model_name="CommittedPrices",
                id_=f"reo_id={reo_id}, distribution_config_id={distribution_config_id}",
            )

        # Parse committed prices using Pydantic models
        premises_with_calculations: list[PremisesWithCalculation] = []
        for cp in committed_prices:
            # cp.content contains the full premise data with calculation
            content = cp.content if hasattr(cp, "content") else {}
            if not isinstance(content, dict):
                continue

            # Validate using PremisesWithCalculation model
            try:
                premise_with_calc = PremisesWithCalculation.model_validate(content)
                premises_with_calculations.append(premise_with_calc)
            except Exception:
                continue

        if not premises_with_calculations:
            raise ObjectNotFound(
                model_name="CommittedPrices",
                id_=f"reo_id={reo_id}, distribution_config_id={distribution_config_id}",
            )

        # Convert to Excel format using PremisesFileSpecificationCreate model
        rows = []
        for premise_with_calc in premises_with_calculations:
            # Unpack premise data (exclude id, reo_id, uploaded, calculation)
            premise_data = premise_with_calc.model_dump(
                exclude={"id", "reo_id", "uploaded", "calculation"}, exclude_none=False
            )

            # Convert entrance from str to int if possible
            if isinstance(premise_data["entrance"], str) and premise_data["entrance"].isdigit():
                premise_data["entrance"] = int(premise_data["entrance"])

            # Convert studio from bool to "Yes"/"No"
            premise_data["studio"] = "Yes" if premise_data["studio"] else "No"

            # Add actual_price_per_sqm from calculation
            if premise_with_calc.calculation and premise_with_calc.calculation.actual_price_per_sqm is not None:
                premise_data["actual_price_per_sqm"] = premise_with_calc.calculation.actual_price_per_sqm

            # Create PremisesFileSpecificationCreate instance using model_construct
            # to work with field names (not aliases) directly
            premise_spec = PremisesFileSpecificationCreate.model_construct(**premise_data)

            # Convert to dict with aliases for Excel and add custom content
            premise_dict = premise_spec.model_dump(by_alias=True, exclude_none=False)

            # Add custom content if exists
            if premise_with_calc.customcontent:
                premise_dict.update(premise_with_calc.customcontent)

            rows.append(premise_dict)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Generate Excel file
        excel_bytes = await self.file_processor.write_excel_file(df)
        return excel_bytes
