from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.base import ApiResponse
from app.schemas.test_run import TestRunCreate, TestRunResponse, TestRunUpdate
from app.services.test_run import TestRunService

router = APIRouter(prefix="/test-runs", tags=["TestRun"])


def get_test_run_service(
    session: AsyncSession = Depends(get_session),
) -> TestRunService:
    """依賴注入：取得 TestRunService 實例。"""
    return TestRunService(session)


@router.get("", response_model=ApiResponse)
async def get_test_runs(
    service: TestRunService = Depends(get_test_run_service),
) -> ApiResponse:
    """取得所有測試批次。"""
    runs = await service.get_all_test_runs()
    return ApiResponse(
        data=[TestRunResponse.model_validate(r) for r in runs],
    )


@router.get("/{test_run_id}", response_model=ApiResponse)
async def get_test_run(
    test_run_id: int,
    service: TestRunService = Depends(get_test_run_service),
) -> ApiResponse:
    """依 ID 取得單筆測試批次。"""
    run = await service.get_test_run(test_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="TestRun not found")
    return ApiResponse(data=TestRunResponse.model_validate(run))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_test_run(
    data: TestRunCreate,
    service: TestRunService = Depends(get_test_run_service),
) -> ApiResponse:
    """建立新測試批次。"""
    run = await service.create_test_run(data)
    return ApiResponse(
        data=TestRunResponse.model_validate(run),
        message="TestRun created",
    )


@router.put("/{test_run_id}", response_model=ApiResponse)
async def update_test_run(
    test_run_id: int,
    data: TestRunUpdate,
    service: TestRunService = Depends(get_test_run_service),
) -> ApiResponse:
    """更新測試批次。"""
    run = await service.update_test_run(test_run_id, data)
    if not run:
        raise HTTPException(status_code=404, detail="TestRun not found")
    return ApiResponse(
        data=TestRunResponse.model_validate(run),
        message="TestRun updated",
    )


@router.delete("/{test_run_id}", response_model=ApiResponse)
async def delete_test_run(
    test_run_id: int,
    service: TestRunService = Depends(get_test_run_service),
) -> ApiResponse:
    """刪除測試批次。"""
    deleted = await service.delete_test_run(test_run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TestRun not found")
    return ApiResponse(message="TestRun deleted")
