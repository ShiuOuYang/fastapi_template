from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """建立 Item 的請求 schema。"""

    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: bool = True


class ItemUpdate(BaseModel):
    """更新 Item 的請求 schema，欄位皆為選填（partial update）。"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = None


class ItemResponse(BaseModel):
    """Item 回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
