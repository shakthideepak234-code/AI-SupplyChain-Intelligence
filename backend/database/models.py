
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    item_id: Mapped[str] = mapped_column(
        String(100), primary_key=True
    )
    dept_id: Mapped[str] = mapped_column(String(50))
    cat_id: Mapped[str] = mapped_column(String(50))


class Store(Base):
    __tablename__ = "stores"

    store_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    state_id: Mapped[str] = mapped_column(String(20))


class WeeklyDemand(Base):
    __tablename__ = "weekly_demand"

    item_id: Mapped[str] = mapped_column(
        ForeignKey("products.item_id"),
        primary_key=True
    )
    store_id: Mapped[str] = mapped_column(
        ForeignKey("stores.store_id"),
        primary_key=True
    )
    week_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    units_sold: Mapped[int] = mapped_column(BigInteger)

    __table_args__ = (
        Index("idx_demand_store_week", "store_id", "week_id"),
        Index("idx_demand_item_week", "item_id", "week_id"),
    )
