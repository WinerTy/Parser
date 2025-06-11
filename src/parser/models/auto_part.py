from .base import BaseSqlModel
from .mixins import IntIdMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint


class AutoPart(BaseSqlModel, IntIdMixin):
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    article: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

    category: Mapped[str] = mapped_column(String(128), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(128), nullable=False)

    product_name: Mapped[str] = mapped_column(String(256), nullable=False)

    count: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
    )
    type_quantity: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint(
            "article", "category", "subcategory", name="article_unique_constraint"
        ),
    )

    def __str__(self) -> str:
        return self.article
