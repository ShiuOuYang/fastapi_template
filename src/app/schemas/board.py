from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BoardCreate(BaseModel):
    """建立板子的請求 schema。"""

    board_name: str
    panel_id: str


class BoardUpdate(BaseModel):
    """更新板子的請求 schema。"""

    board_name: Optional[str] = None
    panel_id: Optional[str] = None


class BoardResponse(BaseModel):
    """板子回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    board_name: str
    panel_id: str
    created_at: Optional[datetime] = None
