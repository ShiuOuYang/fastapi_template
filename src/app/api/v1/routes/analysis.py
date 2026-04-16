from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.base import ApiResponse
from app.services.analysis import AnalysisService

router = APIRouter(prefix="/analysis", tags=["Analysis"])


def get_analysis_service(
    session: AsyncSession = Depends(get_session),
) -> AnalysisService:
    """依賴注入：取得 AnalysisService 實例。"""
    return AnalysisService(session)


@router.get("/{test_run_id}", response_model=ApiResponse)
async def analyze_test_run(
    test_run_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse:
    """
    根據 test_run_id 進行良率分析。

    回傳：總筆數、pass 數、fail 數、yield rate (%)、fail 的 net_name 清單。
    """
    analysis = await service.analyze_test_run(test_run_id)
    return ApiResponse(data=analysis)
