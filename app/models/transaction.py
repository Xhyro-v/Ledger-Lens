import uuid
from sqlalchemy import String, DateTime, func, ForeignKey, Numeric
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.enums.transaction import TransactionStatus, TransactionType


class Transaction(Base):
        __tablename__ = 'transactions'

        id: Mapped[uuid.UUID] = mapped_column(
                UUID(as_uuid=True), 
                primary_key=True, 
                default=uuid.uuid4
            )
        user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)
        date: Mapped[str] = mapped_column(nullable=False)
        amount: Mapped[Decimal] = mapped_column(Numeric(14,2), nullable=False)
        transaction_type: Mapped["TransactionType"] = mapped_column(nullable=False)
        source: Mapped[str] = mapped_column(nullable=False)
        counterparty: Mapped[str] = mapped_column(nullable=True)
        refrence_id: Mapped[int] = mapped_column(index=True, nullable=True)
        image_path: Mapped[str] = mapped_column(nullable=False)
        status: Mapped["TransactionStatus"] = mapped_column(default=TransactionStatus.UNREVIEWED)
        confidence_score: Mapped[float] = mapped_column(nullable=False)
        uploaded_at: Mapped[datetime] = mapped_column(
                                        DateTime(timezone=True),
                                        server_default=func.now()
                                    )

        user = relationship("User", back_populates="transactions")                
        