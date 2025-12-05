import asyncio
import base64

from app.application.api.depends import agent_service_deps, current_user_deps
from app.core.schemas.agents_schemas import ImageData
from fastapi import APIRouter, BackgroundTasks, UploadFile
from starlette import status

router = APIRouter()


@router.get("/best-flat-label/{reo_id}", status_code=status.HTTP_200_OK)
async def get_best_flat_label(
    reo_id: int,
    background_tasks: BackgroundTasks,
    agent_service: agent_service_deps,
    current_user: current_user_deps,
) -> dict:
    """
    Запускает агента для определения лучшего номера квартиры и сохраняет результат в PricingConfig

    """
    background_tasks.add_task(agent_service.run_best_flat_label_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}


@router.get("/best-floor/{reo_id}", status_code=status.HTTP_200_OK)
async def get_best_floor(
    reo_id: int,
    background_tasks: BackgroundTasks,
    agent_service: agent_service_deps,
    current_user: current_user_deps,
) -> dict:
    """
    Запускает агента для определения лучшего этажа и сохраняет результат в PricingConfig

    """
    background_tasks.add_task(agent_service.run_best_floor_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}


async def prepare_images(files: list[UploadFile]) -> list[ImageData]:
    async def file_to_image_data(file: UploadFile) -> ImageData:
        content = await file.read()
        image_data = ImageData(
            base64=base64.b64encode(content).decode("utf-8"),
            content_type=file.content_type,
            file_name=file.filename,
            size=file.size,
        )
        return image_data

    return await asyncio.gather(
        *(file_to_image_data(file) for file in files if file.content_type.startswith("image/"))
    )


@router.post("/layout-evaluator/{reo_id}", status_code=status.HTTP_200_OK)
async def translate_images(
    reo_id: int,
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
    agent_service: agent_service_deps,
    current_user: current_user_deps,
) -> dict:
    """
    Запускает агента для перевода текста на изображениях
    """
    images = await prepare_images(files)
    background_tasks.add_task(
        agent_service.run_layout_evaluator_agent, reo_id=reo_id, user=current_user, images=images
    )
    return {"status": "processing"}
