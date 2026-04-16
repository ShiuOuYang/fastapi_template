from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestRun(Base):
    """測試批次 ORM 模型。"""

    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    board_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("boards.id"), nullable=False
    )
    run_date: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, nullable=True
    )
    operator: Mapped[Optional[str]] = mapped_column(
        sa.NVARCHAR(100), nullable=True
    )
    machine_id: Mapped[Optional[str]] = mapped_column(
        sa.NVARCHAR(100), nullable=True
    )
    status: Mapped[str] = mapped_column(
        sa.NVARCHAR(20), nullable=False, server_default=sa.text("'pending'")
    )

    # relationships
    board: Mapped["Board"] = relationship("Board", back_populates="test_runs")
    probe_results: Mapped[List["ProbeResult"]] = relationship(
        "ProbeResult", back_populates="test_run", lazy="selectin"
    )
