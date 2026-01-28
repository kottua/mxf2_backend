import base64

from app.application.api.depends import (
    current_user_deps,
    distribution_config_service_deps,
    file_processing_service_deps,
    income_plan_service_deps,
    layout_type_attachment_service_deps,
    premises_service_deps,
    pricing_config_service_deps,
    real_estate_object_service_deps,
)
from app.core.schemas.premise_schemas import (
    BulkPremisesCreateRequest,
    LayoutTypeAttachmentCreate,
    LayoutTypeAttachmentResponse,
    PremisesCreate,
    PremisesFileSpecificationResponse,
    PremisesResponse,
    PremisesUpdate,
    WindowViewAttachmentCreate,
    WindowViewAttachmentResponse,
)
from fastapi import APIRouter, UploadFile
from starlette import status
from starlette.responses import Response

router = APIRouter()


@router.post("/upload/specification/{reo_id}", response_model=list[PremisesFileSpecificationResponse])
async def upload_premises_specification(
    reo_id: int,
    file: UploadFile,
    file_processing_service: file_processing_service_deps,
    premises_service: premises_service_deps,
    pricing_config_service: pricing_config_service_deps,
    income_plan_service: income_plan_service_deps,
    distribution_config_service: distribution_config_service_deps,
    current_user: current_user_deps,
) -> list[PremisesFileSpecificationResponse]:
    # Получаем active_plans, если они есть (если нет - используем пустой список)
    active_plans = await income_plan_service.get_active_plan_by_reo_id(reo_id=reo_id)

    # Читаем содержимое файла
    file_content = await file.read()

    # Обрабатываем файл через сервисный слой
    premises_data = await file_processing_service.process_specification(
        file_content=file_content, filename=file.filename or "unknown"
    )

    # Преобразуем данные в PremisesCreate
    premises_create_list = []
    for spec in premises_data:
        spec_dict = spec.model_dump(by_alias=False)
        # Конвертируем entrance из int в str
        if isinstance(spec_dict.get("entrance"), int):
            spec_dict["entrance"] = str(spec_dict["entrance"])
        # Добавляем reo_id из параметра endpoint
        spec_dict["reo_id"] = reo_id

        premises_create_list.append(PremisesCreate(**spec_dict))

    # Создаем помещения
    bulk_request = BulkPremisesCreateRequest(premises=premises_create_list)
    await premises_service.create_bulk_premises(data=bulk_request, user=current_user)

    # Получаем или создаем базовый distribution config
    distribution_config = await distribution_config_service.get_or_create_base_config(user=current_user)

    # Синхронизируем pricing config через сервис
    await pricing_config_service.sync_pricing_config_after_premises_upload(
        reo_id=reo_id,
        premises=premises_create_list,
        active_plans=active_plans,
        distribution_config=distribution_config,
    )

    return premises_data


@router.post("/bulk", response_model=list[PremisesResponse])
async def create_bulk_premises(
    request: BulkPremisesCreateRequest, premises_service: premises_service_deps, current_user: current_user_deps
) -> list[PremisesResponse]:
    premises = await premises_service.create_bulk_premises(data=request, user=current_user)
    return premises


@router.post("/", response_model=PremisesResponse)
async def create_premises(
    request: PremisesCreate, premises_service: premises_service_deps, _: current_user_deps
) -> PremisesResponse:
    premises = await premises_service.create(data=request)
    return premises


@router.get("/{id}", response_model=PremisesResponse)
async def get_premises(id: int, premises_service: premises_service_deps, _: current_user_deps) -> PremisesResponse:
    premises = await premises_service.get(id=id)
    return premises


@router.get("/", response_model=list[PremisesResponse])
async def get_all_premises(premises_service: premises_service_deps, _: current_user_deps) -> list[PremisesResponse]:
    premises = await premises_service.get_all()
    return premises


@router.put("/{id}", response_model=PremisesResponse)
async def update_premises(
    id: int, request: PremisesUpdate, premises_service: premises_service_deps, _: current_user_deps
) -> PremisesResponse:
    premises = await premises_service.update(id=id, data=request)
    return premises


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_premises(id: int, premises_service: premises_service_deps, _: current_user_deps) -> None:
    await premises_service.delete(id=id)


@router.get("/download/excel/{reo_id}/{distribution_config_id}")
async def download_premises_excel_with_actual_price(
    reo_id: int,
    distribution_config_id: int,
    file_processing_service: file_processing_service_deps,
    # _: current_user_deps,
) -> Response:
    """
    Download Excel file with premises data and actual_price_per_sqm from committed prices.

    Args:
        reo_id: Real estate object ID
        distribution_config_id: Distribution config ID

    Returns:
        Excel file as downloadable response
    """
    excel_bytes = await file_processing_service.generate_excel_with_actual_price(
        reo_id=reo_id, distribution_config_id=distribution_config_id
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=premises_with_actual_price_reo_{reo_id}_dist_{distribution_config_id}.xlsx"
        },
    )


@router.post("/layout-attachments/{reo_id}/{layout_type}", response_model=LayoutTypeAttachmentResponse)
async def upload_layout_type_attachment(
    reo_id: int,
    layout_type: str,
    file: UploadFile,
    attachment_service: layout_type_attachment_service_deps,
    real_estate_object_service: real_estate_object_service_deps,
    current_user: current_user_deps,
) -> LayoutTypeAttachmentResponse:

    reo = await real_estate_object_service.get_full(id=reo_id, user=current_user)

    file_content = await file.read()

    attachment_data = LayoutTypeAttachmentCreate(
        reo_id=reo.id,
        layout_type=layout_type,
        base64_file=base64.b64encode(file_content).decode("utf-8"),
        content_type=file.content_type or "image/jpeg",
        file_name=file.filename or "layout_image",
        file_size=file.size,
    )

    attachment = await attachment_service.update_or_create_layout_type(
        reo_id=reo_id, layout_type=layout_type, data=attachment_data
    )

    return attachment


@router.delete("/layout-attachments/{reo_id}/{layout_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_layout_attachment(
    reo_id: int,
    layout_type: str,
    attachment_service: layout_type_attachment_service_deps,
    _: current_user_deps,
) -> None:

    await attachment_service.delete_layout_type(reo_id=reo_id, layout_type=layout_type)


@router.post("/window-view-attachments/{reo_id}/{view_from_window}", response_model=WindowViewAttachmentResponse)
async def upload_window_view_attachment(
    reo_id: int,
    view_from_window: str,
    file: UploadFile,
    attachment_service: layout_type_attachment_service_deps,
    real_estate_object_service: real_estate_object_service_deps,
    current_user: current_user_deps,
) -> WindowViewAttachmentResponse:

    reo = await real_estate_object_service.get_full(id=reo_id, user=current_user)

    file_content = await file.read()

    attachment_data = WindowViewAttachmentCreate(
        reo_id=reo.id,
        view_from_window=view_from_window,
        base64_file=base64.b64encode(file_content).decode("utf-8"),
        content_type=file.content_type or "image/jpeg",
        file_name=file.filename or "window_view_image",
        file_size=file.size,
    )

    attachment = await attachment_service.update_or_create_window_view(
        reo_id=reo_id, view_from_window=view_from_window, data=attachment_data
    )

    return attachment


@router.delete("/window-view-attachments/{reo_id}/{view_from_window}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_window_view_attachment(
    reo_id: int,
    view_from_window: str,
    attachment_service: layout_type_attachment_service_deps,
    _: current_user_deps,
) -> None:

    await attachment_service.delete_view_from_window(reo_id=reo_id, view_from_window=view_from_window)
