from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ProbeResultCreate(BaseModel):
    """建立單筆飛針量測結果的請求 schema。"""

    test_run_id: int
    net_name: str
    x1: float
    y1: float
    x2: float
    y2: float
    measured_value: float
    spec_min: float
    spec_max: float
    pass_fail: bool


class ProbeResultBulkCreate(BaseModel):
    """批次寫入飛針量測結果的請求 schema。"""

    items: List[ProbeResultCreate]


class ProbeResultResponse(BaseModel):
    """飛針量測結果回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    test_run_id: int
    net_name: str
    x1: float
    y1: float
    x2: float
    y2: float
    measured_value: float
    spec_min: float
    spec_max: float
    pass_fail: bool
    created_at: Optional[datetime] = None
