from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Board(Base):
    """板子 ORM 模型。"""

    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    board_name: Mapped[str] = mapped_column(sa.NVARCHAR(200), nullable=False)
    panel_id: Mapped[str] = mapped_column(sa.NVARCHAR(200), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, server_default=sa.text("GETDATE()"), nullable=True
    )

    # relationships
    test_runs: Mapped[List["TestRun"]] = relationship(
        "TestRun", back_populates="board", lazy="selectin"
    )
