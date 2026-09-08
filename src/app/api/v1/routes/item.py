from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import SessionDep
from app.schemas.base import ApiResponse, Page
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item import ItemService

router = APIRouter(prefix="/items", tags=["Item"])


def get_item_service(session: SessionDep) -> ItemService:
    """依賴注入：取得 ItemService 實例。"""
    return ItemService(session)


ServiceDep = Depends(get_item_service)


@router.get("", response_model=ApiResponse, summary="查詢 Item 清單")
async def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    service: ItemService = ServiceDep,
) -> ApiResponse:
    """分頁取得所有 Item。"""
    items, total = await service.list_items(skip=skip, limit=limit)
    page = Page[ItemResponse](
        items=[ItemResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )
    return ApiResponse(data=page)


@router.get("/{item_id}", response_model=ApiResponse, summary="查詢單筆 Item")
async def get_item(
    item_id: int,
    service: ItemService = ServiceDep,
) -> ApiResponse:
    """依 ID 取得單筆 Item。"""
    item = await service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ApiResponse(data=ItemResponse.model_validate(item))


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="建立 Item",
)
async def create_item(
    data: ItemCreate,
    service: ItemService = ServiceDep,
) -> ApiResponse:
    """建立新的 Item。"""
    item = await service.create_item(data)
    return ApiResponse(
        data=ItemResponse.model_validate(item),
        message="Item created",
    )


@router.patch("/{item_id}", response_model=ApiResponse, summary="部分更新 Item")
async def update_item(
    item_id: int,
    data: ItemUpdate,
    service: ItemService = ServiceDep,
) -> ApiResponse:
    """只更新有帶到的欄位。"""
    item = await service.update_item(item_id, data)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ApiResponse(
        data=ItemResponse.model_validate(item),
        message="Item updated",
    )


@router.delete("/{item_id}", response_model=ApiResponse, summary="刪除 Item")
async def delete_item(
    item_id: int,
    service: ItemService = ServiceDep,
) -> ApiResponse:
    """依 ID 刪除 Item。"""
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return ApiResponse(message="Item deleted")
