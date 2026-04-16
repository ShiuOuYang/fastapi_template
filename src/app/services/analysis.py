from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.probe_result import ProbeResultRepository
from app.schemas.analysis import AnalysisResponse


class AnalysisService:
    """良率分析商業邏輯層（純運算，不入 DB）。"""

    def __init__(self, session: AsyncSession) -> None:
        self.probe_result_repo = ProbeResultRepository(session)

    async def analyze_test_run(self, test_run_id: int) -> AnalysisResponse:
        """
        根據 test_run_id 計算良率分析。

        Returns:
            AnalysisResponse 包含總筆數、pass/fail 數、yield rate、fail net_name 清單。
        """
        results = await self.probe_result_repo.get_by_test_run_id(test_run_id)
        total = len(results)
        pass_count = sum(1 for r in results if r.pass_fail)
        fail_count = total - pass_count
        yield_rate = round((pass_count / total * 100), 2) if total > 0 else 0.0
        fail_net_names: List[str] = list(
            set(r.net_name for r in results if not r.pass_fail)
        )
        return AnalysisResponse(
            test_run_id=test_run_id,
            total_count=total,
            pass_count=pass_count,
            fail_count=fail_count,
            yield_rate=yield_rate,
            fail_net_names=fail_net_names,
        )
