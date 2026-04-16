from __future__ import annotations

from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProbeResult(Base):
    """飛針量測結果 ORM 模型。"""

    __tablename__ = "probe_results"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    test_run_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("test_runs.id"), nullable=False
    )
    net_name: Mapped[str] = mapped_column(sa.NVARCHAR(200), nullable=False)
    x1: Mapped[float] = mapped_column(sa.Float, nullable=False)
    y1: Mapped[float] = mapped_column(sa.Float, nullable=False)
    x2: Mapped[float] = mapped_column(sa.Float, nullable=False)
    y2: Mapped[float] = mapped_column(sa.Float, nullable=False)
    measured_value: Mapped[float] = mapped_column(sa.Float, nullable=False)
    spec_min: Mapped[float] = mapped_column(sa.Float, nullable=False)
    spec_max: Mapped[float] = mapped_column(sa.Float, nullable=False)
    pass_fail: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, server_default=sa.text("GETDATE()"), nullable=True
    )

    # relationships
    test_run: Mapped["TestRun"] = relationship(
        "TestRun", back_populates="probe_results"
    )
