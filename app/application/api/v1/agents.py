from app.application.api.depends import agent_service_deps, current_user_deps
from fastapi import APIRouter, BackgroundTasks
from starlette import status

router = APIRouter()


@router.post("/best-flat-label/{reo_id}", status_code=status.HTTP_200_OK)
async def best_flat_label(
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


@router.post("/best-floor/{reo_id}", status_code=status.HTTP_200_OK)
async def best_floor(
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


@router.post("/layout-evaluator/{reo_id}", status_code=status.HTTP_200_OK)
async def translate_images(
    reo_id: int,
    background_tasks: BackgroundTasks,
    agent_service: agent_service_deps,
    current_user: current_user_deps,
) -> dict:
    """
    Запускает агента для перевода текста на изображениях
    """
    background_tasks.add_task(agent_service.run_layout_evaluator_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}


@router.post("/window-view-evaluator/{reo_id}", status_code=status.HTTP_200_OK)
async def window_view_evaluator(
    reo_id: int, background_tasks: BackgroundTasks, agent_service: agent_service_deps, current_user: current_user_deps
) -> dict:
    """
    Запускает агента для оценки вида из окна
    """
    background_tasks.add_task(agent_service.run_window_view_evaluator_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}


@router.post("/total_area-evaluator/{reo_id}", status_code=status.HTTP_200_OK)
async def total_area_evaluator(
    reo_id: int, background_tasks: BackgroundTasks, agent_service: agent_service_deps, current_user: current_user_deps
) -> dict:
    """
    Запускает агента для оценки общей площади
    """
    background_tasks.add_task(agent_service.run_total_area_evaluator_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}


@router.post("/best-entrance/{reo_id}", status_code=status.HTTP_200_OK)
async def best_entrance_evaluator(
    reo_id: int, background_tasks: BackgroundTasks, agent_service: agent_service_deps, current_user: current_user_deps
) -> dict:
    """
    Запускает агента для определения лучшего подъезда и сохраняет результат в PricingConfig

    """
    background_tasks.add_task(agent_service.run_best_entrance_agent, reo_id=reo_id, user=current_user)
    return {"status": "processing"}
