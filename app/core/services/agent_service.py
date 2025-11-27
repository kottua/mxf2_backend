import asyncio

from app.core.exceptions import AgentExecutionError, AgentNotFound
from app.core.schemas.user_schemas import UserOutputSchema
from app.core.services.pricing_config_service import PricingConfigService
from app.core.services.real_estate_object_service import RealEstateObjectService
from app.infrastructure.agents.agent_constants import AgentID
from app.infrastructure.agents.agent_manager import AgentManager
from app.infrastructure.agents.prompt_manager import prompt_manager


class AgentService:
    def __init__(
        self,
        agent_manager: AgentManager,
        real_estate_object_service: RealEstateObjectService,
        pricing_config_service: PricingConfigService,
    ):
        self.agent_manager = agent_manager
        self.real_estate_object_service = real_estate_object_service
        self.pricing_config_service = pricing_config_service

    def _run_blocking_agent(self, agent_id: AgentID, user_prompt: str) -> dict:
        if self.agent_manager.get_agent(agent_id) is None:
            raise AgentNotFound(agent_id=agent_id)

        result = self.agent_manager.run_agent(agent_id, user_input=user_prompt)

        if result is None:
            raise AgentExecutionError(agent_id=agent_id)

        return result.model_dump()

    async def run_best_flat_label_agent(self, reo_id: int, user: UserOutputSchema) -> None:

        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        flat_numbers = [premise.number for premise in reo.premises]
        user_prompt = prompt_manager.USER_PROMPT_BEST_FLAT_LABEL.format(flat_numbers=flat_numbers)

        result_dict = await asyncio.to_thread(self._run_blocking_agent, AgentID.BEST_FLAT_LABEL, user_prompt)

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
