from pydantic import BaseModel, EmailStr


class UserInputSchema(BaseModel):
    """Schema for user input data."""

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: str


class UserOutputSchema(BaseModel):
    """Schema for user output data."""

    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    """Schema for updating user data."""

    first_name: str | None = None
    last_name: str | None = None


class UserPasswordUpdateSchema(BaseModel):
    """Schema for updating user password."""

    old_password: str
    new_password: str

    class Config:
        str_min_length = 1  # Ensure that passwords are not empty


class ResetPasswordSchema(BaseModel):
    """Schema for resetting user password."""

    new_password: str

    class Config:
        str_min_length = 1


class ApiTokenSchema(BaseModel):
    access_token: str


class ApiTokenInputSchema(BaseModel):
    """Schema for API token."""

    key_name: str


class ApiTokenOutputSchema(ApiTokenInputSchema, ApiTokenSchema):
    """Schema for API token."""

    pass
