from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.probe_result import ProbeResult
from app.repositories.probe_result import ProbeResultRepository
from app.schemas.probe_result import ProbeResultCreate


class ProbeResultService:
    """ProbeResult 商業邏輯層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ProbeResultRepository(session)

    async def get_probe_result(self, result_id: int) -> Optional[ProbeResult]:
        """取得單筆 ProbeResult。"""
        return await self.repository.get_by_id(result_id)

    async def get_by_test_run(
        self,
        test_run_id: int,
        pass_fail: Optional[bool] = None,
    ) -> List[ProbeResult]:
        """依 test_run_id 查詢量測結果，可選擇 pass/fail 過濾。"""
        return await self.repository.get_by_test_run_id(
            test_run_id, pass_fail=pass_fail
        )

    async def create_probe_result(self, data: ProbeResultCreate) -> ProbeResult:
        """建立單筆 ProbeResult。"""
        probe_result = ProbeResult(
            test_run_id=data.test_run_id,
            net_name=data.net_name,
            x1=data.x1,
            y1=data.y1,
            x2=data.x2,
            y2=data.y2,
            measured_value=data.measured_value,
            spec_min=data.spec_min,
            spec_max=data.spec_max,
            pass_fail=data.pass_fail,
        )
        return await self.repository.create(probe_result)

    async def bulk_create(self, items: List[ProbeResultCreate]) -> int:
        """
        批次寫入多筆 ProbeResult。

        Returns:
            寫入的筆數。
        """
        probe_results = [
            ProbeResult(
                test_run_id=item.test_run_id,
                net_name=item.net_name,
                x1=item.x1,
                y1=item.y1,
                x2=item.x2,
                y2=item.y2,
                measured_value=item.measured_value,
                spec_min=item.spec_min,
                spec_max=item.spec_max,
                pass_fail=item.pass_fail,
            )
            for item in items
        ]
        return await self.repository.bulk_create(probe_results)
