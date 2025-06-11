from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class IntIdMixin:
    """Mixin class for add field 'id' as primary key"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
