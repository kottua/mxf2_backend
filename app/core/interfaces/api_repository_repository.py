from abc import ABC, abstractmethod
from typing import Any


class ApiRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> None:
        raise NotImplementedError
