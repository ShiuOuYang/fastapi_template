from __future__ import annotations

from typing import List

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    """良率分析回應 schema（純運算，不入 DB）。"""

    test_run_id: int
    total_count: int
    pass_count: int
    fail_count: int
    yield_rate: float
    fail_net_names: List[str]
