from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.base import ApiResponse
from app.schemas.probe_result import (
    ProbeResultBulkCreate,
    ProbeResultCreate,
    ProbeResultResponse,
)
from app.services.probe_result import ProbeResultService

router = APIRouter(prefix="/probe-results", tags=["ProbeResult"])


def get_probe_result_service(
    session: AsyncSession = Depends(get_session),
) -> ProbeResultService:
    """依賴注入：取得 ProbeResultService 實例。"""
    return ProbeResultService(session)


@router.get("", response_model=ApiResponse)
async def get_probe_results_by_test_run(
    test_run_id: int = Query(..., description="測試批次 ID"),
    pass_fail: Optional[bool] = Query(None, description="依 pass/fail 過濾"),
    service: ProbeResultService = Depends(get_probe_result_service),
) -> ApiResponse:
    """依 test_run_id 查詢量測結果，可選擇 pass/fail 過濾。"""
    results = await service.get_by_test_run(
        test_run_id, pass_fail=pass_fail
    )
    return ApiResponse(
        data=[ProbeResultResponse.model_validate(r) for r in results],
    )


@router.get("/{result_id}", response_model=ApiResponse)
async def get_probe_result(
    result_id: int,
    service: ProbeResultService = Depends(get_probe_result_service),
) -> ApiResponse:
    """依 ID 取得單筆量測結果。"""
    result = await service.get_probe_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="ProbeResult not found")
    return ApiResponse(data=ProbeResultResponse.model_validate(result))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_probe_result(
    data: ProbeResultCreate,
    service: ProbeResultService = Depends(get_probe_result_service),
) -> ApiResponse:
    """建立單筆量測結果。"""
    result = await service.create_probe_result(data)
    return ApiResponse(
        data=ProbeResultResponse.model_validate(result),
        message="ProbeResult created",
    )


@router.post("/bulk", response_model=ApiResponse, status_code=201)
async def bulk_create_probe_results(
    data: ProbeResultBulkCreate,
    service: ProbeResultService = Depends(get_probe_result_service),
) -> ApiResponse:
    """批次寫入多筆量測結果。"""
    count = await service.bulk_create(data.items)
    return ApiResponse(
        data={"inserted_count": count},
        message="Bulk insert completed",
    )
