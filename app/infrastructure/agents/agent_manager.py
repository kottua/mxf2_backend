from typing import Any, Type

from app.core.schemas import agents_schemas
from app.infrastructure.agents.agent_constants import AgentID
from app.infrastructure.agents.base_agent import BaseAgent
from app.infrastructure.agents.prompt_manager import prompt_manager
from app.settings import AgentConfig
from pydantic import BaseModel


class AgentDefinition:
    """Определение агента с его промптами и моделью ответа"""

    def __init__(
        self,
        agent_id: str,
        system_prompt: str,
        response_model: Type[BaseModel],
    ):
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.response_model = response_model


class AgentManager:
    _INSTANCE = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "AgentManager":
        if cls._INSTANCE is None:
            cls._INSTANCE = super(AgentManager, cls).__new__(cls)
        return cls._INSTANCE

    def __init__(self, config: AgentConfig):
        self.config = config
        self._agents: dict[str, BaseAgent] = {}
        self._agent_definitions: dict[str, AgentDefinition] = {}
        self._register_all_agents()

    def register_agent(self, definition: AgentDefinition) -> None:
        """Регистрирует нового агента"""
        agent = BaseAgent(
            config=self.config,
            system_prompt=definition.system_prompt,
            response_model=definition.response_model,
        )
        self._agents[definition.agent_id] = agent
        self._agent_definitions[definition.agent_id] = definition

    def get_agent(self, agent_id: str) -> BaseAgent | None:
        """Получает агента по ID"""
        return self._agents.get(agent_id)

    def run_agent(self, agent_id: str, user_input: str) -> BaseModel | None:
        """Запускает агента с переданным user_input"""
        agent = self.get_agent(agent_id)
        if agent is None:
            return None
        return agent.run(user_input)

    def list_agents(self) -> list[str]:
        """Возвращает список всех зарегистрированных агентов"""
        return list(self._agents.keys())

    def _register_all_agents(self) -> None:
        """Регистрирует всех агентов в системе"""

        self._register_best_flat_label_agent()
        self._register_best_flat_floor_agent()

    def _register_best_flat_label_agent(self) -> None:
        """Регистрирует тестового агента для определения лучшей квартиры"""
        definition = AgentDefinition(
            agent_id=AgentID.BEST_FLAT_LABEL,
            system_prompt=prompt_manager.SYSTEM_PROMPT_BEST_FLAT_LABEL,
            response_model=agents_schemas.BestFlatLabelResponse,
        )
        self.register_agent(definition)

    def _register_best_flat_floor_agent(self) -> None:
        """Регистрирует тестового агента для определения лучшего этажа квартиры"""
        definition = AgentDefinition(
            agent_id=AgentID.BEST_FLAT_FLOOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_BEST_FLAT_FLOOR,
            response_model=agents_schemas.BestFlatFloorResponse,
        )
        self.register_agent(definition)
