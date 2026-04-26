from sqlalchemy import func, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from db.database import Base
from datetime import datetime


class Role(str, Enum):
    CLIENT = "Client"
    WORKER = "Worker"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column( index=True, nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.CLIENT, nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)

    def __repr__(self):
        return f"{self.name}, {self.role}"
    

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="wallet")
    balance: Mapped[float] = mapped_column(default=0)

    def __repr__(self):
        return f"{self.user_id}, {self.balance}"





