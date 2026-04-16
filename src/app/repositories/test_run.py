from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_run import TestRun


class TestRunRepository:
    """TestRun 資料存取層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, test_run_id: int) -> Optional[TestRun]:
        """依 ID 查詢單筆 TestRun。"""
        result = await self.session.execute(
            select(TestRun).where(TestRun.id == test_run_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[TestRun]:
        """查詢所有 TestRun。"""
        result = await self.session.execute(select(TestRun))
        return list(result.scalars().all())

    async def create(self, test_run: TestRun) -> TestRun:
        """新增一筆 TestRun。"""
        self.session.add(test_run)
        await self.session.flush()
        await self.session.refresh(test_run)
        return test_run

    async def update(self, test_run: TestRun) -> TestRun:
        """更新 TestRun（呼叫前請先修改屬性）。"""
        await self.session.flush()
        await self.session.refresh(test_run)
        return test_run

    async def delete(self, test_run: TestRun) -> None:
        """刪除一筆 TestRun。"""
        await self.session.delete(test_run)
        await self.session.flush()
