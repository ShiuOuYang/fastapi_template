from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TestRunStatus(str, Enum):
    """測試批次狀態列舉。"""

    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class TestRunCreate(BaseModel):
    """建立測試批次的請求 schema。"""

    board_id: int
    run_date: Optional[datetime] = None
    operator: Optional[str] = None
    machine_id: Optional[str] = None
    status: TestRunStatus = TestRunStatus.pending


class TestRunUpdate(BaseModel):
    """更新測試批次的請求 schema。"""

    board_id: Optional[int] = None
    run_date: Optional[datetime] = None
    operator: Optional[str] = None
    machine_id: Optional[str] = None
    status: Optional[TestRunStatus] = None


class TestRunResponse(BaseModel):
    """測試批次回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    board_id: int
    run_date: Optional[datetime] = None
    operator: Optional[str] = None
    machine_id: Optional[str] = None
    status: str
