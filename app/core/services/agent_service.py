import asyncio

from app.core.exceptions import AgentExecutionError, AgentNotFound
from app.core.schemas.agents_schemas import ImageData
from app.core.schemas.user_schemas import UserOutputSchema
from app.core.services.pricing_config_service import PricingConfigService
from app.core.services.real_estate_object_service import RealEstateObjectService
from app.infrastructure.agents.agent_constants import AgentID
from app.infrastructure.agents.agent_manager import AgentManager
from app.infrastructure.agents.prompt_manager import prompt_manager
from loguru import logger


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

    def _run_blocking_agent(self, agent_id: AgentID, user_prompt: str, images: list[ImageData] | None = None) -> dict:
        if self.agent_manager.get_agent(agent_id) is None:
            raise AgentNotFound(agent_id=agent_id)

        result = self.agent_manager.run_agent(agent_id, user_input=user_prompt, images=images)

        if result is None:
            raise AgentExecutionError(agent_id=agent_id)

        return result.model_dump()

    async def run_best_flat_label_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info(f"Running best label agent for REO ID: {reo_id}")

        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        flat_numbers = [premise.number for premise in reo.premises]
        user_prompt = prompt_manager.USER_PROMPT_BEST_FLAT_LABEL.format(flat_numbers=flat_numbers)

        result_dict = await asyncio.to_thread(self._run_blocking_agent, AgentID.BEST_FLAT_LABEL, user_prompt)

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info(f"Finished running best label agent for REO ID: {reo_id}")

    async def run_best_floor_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info(f"Running best floor agent for REO ID: {reo_id}")

        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        floor_numbers = sorted({premise.floor for premise in reo.premises})
        user_prompt = prompt_manager.USER_PROMPT_BEST_FLAT_FLOOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class, floors=floor_numbers
        )

        result_dict = await asyncio.to_thread(self._run_blocking_agent, AgentID.BEST_FLAT_FLOOR, user_prompt)

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info(f"Finished running best floor agent for REO ID: {reo_id}")

    async def run_layout_evaluator_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running layout evaluator agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        user_prompt = prompt_manager.USER_PROMPT_LAYOUT_EVALUATOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class
        )
        images: list[ImageData] = []

        for image_attachment in reo.layout_type_attachments:
            image = ImageData(
                layout_type=image_attachment.layout_type,
                base64=image_attachment.base64_file,
                content_type=image_attachment.content_type,
                file_name=image_attachment.file_name,
                size=image_attachment.file_size,
            )
            images.append(image)

        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.LAYOUT_EVALUATOR, user_prompt=user_prompt, images=images
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running layout evaluator agent")
