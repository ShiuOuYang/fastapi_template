from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.probe_result import ProbeResult


class ProbeResultRepository:
    """ProbeResult 資料存取層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, result_id: int) -> Optional[ProbeResult]:
        """依 ID 查詢單筆 ProbeResult。"""
        result = await self.session.execute(
            select(ProbeResult).where(ProbeResult.id == result_id)
        )
        return result.scalar_one_or_none()

    async def get_by_test_run_id(
        self,
        test_run_id: int,
        pass_fail: Optional[bool] = None,
    ) -> List[ProbeResult]:
        """
        依 test_run_id 查詢量測結果。

        Args:
            test_run_id: 測試批次 ID。
            pass_fail: 若指定，則依 pass/fail 過濾。
        """
        stmt = select(ProbeResult).where(
            ProbeResult.test_run_id == test_run_id
        )
        if pass_fail is not None:
            stmt = stmt.where(ProbeResult.pass_fail == pass_fail)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, probe_result: ProbeResult) -> ProbeResult:
        """新增一筆 ProbeResult。"""
        self.session.add(probe_result)
        await self.session.flush()
        await self.session.refresh(probe_result)
        return probe_result

    async def bulk_create(self, probe_results: List[ProbeResult]) -> int:
        """
        批次寫入多筆 ProbeResult。

        Returns:
            寫入的筆數。
        """
        self.session.add_all(probe_results)
        await self.session.flush()
        return len(probe_results)
