from app.application.api.depends import agent_service_deps, current_user_deps
from fastapi import APIRouter, BackgroundTasks
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
