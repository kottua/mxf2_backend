from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import EmailStr


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, user_payload: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get(self, email: EmailStr) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: Any, updates: Dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_password(self, user: Any, new_password: str) -> None:
        raise NotImplementedError
