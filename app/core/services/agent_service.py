import asyncio
import json

from app.core.exceptions import AgentExecutionError, AgentNotFound
from app.core.schemas.agents_schemas import FilesData, ValidAgentFields
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

    def _run_blocking_agent(self, agent_id: AgentID, user_prompt: str, files: list[FilesData] | None = None) -> dict:
        if self.agent_manager.get_agent(agent_id) is None:
            raise AgentNotFound(agent_id=agent_id)

        result = self.agent_manager.run_agent(agent_id, user_input=user_prompt, files=files)

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
        files: list[FilesData] = []

        for file_attachment in reo.layout_type_attachments:
            file = FilesData(
                layout_type=file_attachment.layout_type,
                base64=file_attachment.base64_file,
                content_type=file_attachment.content_type,
                file_name=file_attachment.file_name,
                size=file_attachment.file_size,
            )
            files.append(file)

        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.LAYOUT_EVALUATOR, user_prompt=user_prompt, files=files
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running layout evaluator agent")

    async def run_window_view_evaluator_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running window view evaluator agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        user_prompt = prompt_manager.USER_PROMPT_WINDOW_VIEW_EVALUATOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class
        )

        files: list[FilesData] = []

        for file_attachment in reo.window_view_attachments:
            file = FilesData(
                view_from_window=file_attachment.view_from_window,
                base64=file_attachment.base64_file,
                content_type=file_attachment.content_type,
                file_name=file_attachment.file_name,
                size=file_attachment.file_size,
            )
            files.append(file)

        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.WINDOW_VIEW_EVALUATOR, user_prompt=user_prompt, files=files
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running layout evaluator agent")

    async def run_total_area_evaluator_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running total area evaluator agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        total_areas = sorted({premise.total_area_m2 for premise in reo.premises})
        user_prompt = prompt_manager.USER_PROMPT_TOTAL_AREA_EVALUATOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class, total_areas=total_areas
        )
        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.TOTAL_AREA_EVALUATOR, user_prompt=user_prompt
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running total area evaluator agent")

    async def run_best_entrance_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running best entrance agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)
        entrances = set(prem.entrance for prem in reo.premises)
        entrance_result = []
        for entrance in entrances:
            apartments = [p for p in reo.premises if p.entrance == entrance]
            floors = {p.floor for p in apartments}

            entrance_result.append(
                {
                    "entrance_number": entrance,
                    "apartments_in_entrance": len(apartments),
                    "floors_in_entrance": len(floors),
                }
            )

        entrance_json = json.dumps(entrance_result, ensure_ascii=False)
        user_prompt = prompt_manager.USER_PROMPT_ENTRANCE_EVALUATOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class, entrance_result=entrance_json
        )
        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.ENTRANCE_EVALUATOR, user_prompt=user_prompt
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running best entrance agent")

    async def run_room_quantity_evaluator_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running room quantity agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)
        possible_values = []

        for premise in reo.premises:
            rooms = premise.number_of_rooms or 0
            if premise.studio:
                isolated_bedroom = 0
            else:
                isolated_bedroom = rooms
            possible_values.append(isolated_bedroom)

        unique_values = sorted(set(possible_values))

        user_prompt = prompt_manager.USER_PROMPT_ROOM_QUANTITY_EVALUATOR.format(
            latitude=reo.lat, longitude=reo.lon, object_class=reo.property_class, isolated_bedroom=unique_values
        )
        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.ROOM_EVALUATOR, user_prompt=user_prompt
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running best entrance agent")

    async def run_weighted_factors_agent(self, reo_id: int, user: UserOutputSchema) -> None:
        logger.info("Running weighted factors agent")
        reo = await self.real_estate_object_service.get_full(id=reo_id, user=user)

        user_prompt = prompt_manager.USER_PROMPT_WEIGHTED_FACTORS_EVALUATOR.format(
            latitude=reo.lat,
            longitude=reo.lon,
            object_class=reo.property_class,
            available_fields_list=ValidAgentFields.to_prompt_string(),
        )
        result_dict = await asyncio.to_thread(
            self._run_blocking_agent, AgentID.WEIGHTED_FACTORS, user_prompt=user_prompt
        )

        await self.pricing_config_service.update_reo_pricing_config(reo_id=reo_id, data=result_dict)
        logger.info("Finished running weighted factors agent")
