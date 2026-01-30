from typing import Any, Type

from app.core.schemas import agents_schemas
from app.core.schemas.agents_schemas import FilesData
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
        self.__register_all_agents()

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

    def run_agent(self, agent_id: str, user_input: str, files: list[FilesData] | None = None) -> BaseModel | None:
        """Запускает агента с переданным user_input"""
        agent = self.get_agent(agent_id)
        if agent is None:
            return None
        return agent.run(user_input, files=files)

    def list_agents(self) -> list[str]:
        """Возвращает список всех зарегистрированных агентов"""
        return list(self._agents.keys())

    def __register_all_agents(self) -> None:
        """Регистрирует всех агентов в системе"""
        methods = [
            getattr(self, name)
            for name in dir(self)
            if name.startswith("_register_") and callable(getattr(self, name))
        ]

        for method in methods:
            method()

    def _register_best_flat_label_agent(self) -> None:
        """Регистрирует агента для определения лучшей квартиры"""
        definition = AgentDefinition(
            agent_id=AgentID.BEST_FLAT_LABEL,
            system_prompt=prompt_manager.SYSTEM_PROMPT_BEST_FLAT_LABEL,
            response_model=agents_schemas.BestFlatLabelResponse,
        )
        self.register_agent(definition)

    def _register_best_flat_floor_agent(self) -> None:
        """Регистрирует агента для определения лучшего этажа квартиры"""
        definition = AgentDefinition(
            agent_id=AgentID.BEST_FLAT_FLOOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_BEST_FLAT_FLOOR,
            response_model=agents_schemas.BestFlatFloorResponse,
        )
        self.register_agent(definition)

    def _register_layout_evaluator_agent(self) -> None:
        """Регистрирует агента для оценки планировки"""
        definition = AgentDefinition(
            agent_id=AgentID.LAYOUT_EVALUATOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_LAYOUT_EVALUATOR,
            response_model=agents_schemas.LayoutEvaluatorResponse,
        )
        self.register_agent(definition)

    def _register_window_view_evaluator_agent(self) -> None:
        definition = AgentDefinition(
            agent_id=AgentID.WINDOW_VIEW_EVALUATOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_WINDOW_VIEW_EVALUATOR,
            response_model=agents_schemas.WindowViewEvaluatorResponse,
        )
        self.register_agent(definition)

    def _register_total_area_evaluator_agent(self) -> None:
        definition = AgentDefinition(
            agent_id=AgentID.TOTAL_AREA_EVALUATOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_TOTAL_AREA_EVALUATOR,
            response_model=agents_schemas.TotalAreaEvaluatorResponse,
        )
        self.register_agent(definition)

    def _register_entrance_evaluator_agent(self) -> None:
        definition = AgentDefinition(
            agent_id=AgentID.ENTRANCE_EVALUATOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_ENTRANCE_EVALUATOR,
            response_model=agents_schemas.EntranceEvaluatorResponse,
        )
        self.register_agent(definition)

    def _register_room_evaluator_agent(self) -> None:
        definition = AgentDefinition(
            agent_id=AgentID.ROOM_EVALUATOR,
            system_prompt=prompt_manager.SYSTEM_PROMPT_ROOM_QUANTITY_EVALUATOR,
            response_model=agents_schemas.RoomEvaluatorResponse,
        )
        self.register_agent(definition)

    def _register_weighted_factors_agent(self) -> None:
        definition = AgentDefinition(
            agent_id=AgentID.WEIGHTED_FACTORS,
            system_prompt=prompt_manager.SYSTEM_PROMPT_WEIGHTED_FACTORS_EVALUATOR,
            response_model=agents_schemas.WeightedFactorsResponse,
        )
        self.register_agent(definition)
