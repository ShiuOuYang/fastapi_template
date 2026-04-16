from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_run import TestRun
from app.repositories.test_run import TestRunRepository
from app.schemas.test_run import TestRunCreate, TestRunUpdate


class TestRunService:
    """TestRun 商業邏輯層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = TestRunRepository(session)

    async def get_test_run(self, test_run_id: int) -> Optional[TestRun]:
        """取得單筆 TestRun。"""
        return await self.repository.get_by_id(test_run_id)

    async def get_all_test_runs(self) -> List[TestRun]:
        """取得所有 TestRun。"""
        return await self.repository.get_all()

    async def create_test_run(self, data: TestRunCreate) -> TestRun:
        """建立新 TestRun。"""
        test_run = TestRun(
            board_id=data.board_id,
            run_date=data.run_date,
            operator=data.operator,
            machine_id=data.machine_id,
            status=data.status.value,
        )
        return await self.repository.create(test_run)

    async def update_test_run(
        self, test_run_id: int, data: TestRunUpdate
    ) -> Optional[TestRun]:
        """更新 TestRun，若不存在回傳 None。"""
        test_run = await self.repository.get_by_id(test_run_id)
        if not test_run:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value if hasattr(value, "value") else value
            setattr(test_run, field, value)
        return await self.repository.update(test_run)

    async def delete_test_run(self, test_run_id: int) -> bool:
        """刪除 TestRun，回傳是否成功。"""
        test_run = await self.repository.get_by_id(test_run_id)
        if not test_run:
            return False
        await self.repository.delete(test_run)
        return True
