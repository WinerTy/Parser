from sqlalchemy.orm import DeclarativeBase, declared_attr

from utils import camel_case_to_snake_case

from core import conf
from sqlalchemy import MetaData


class BaseSqlModel(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=conf.db.naming_convention)

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        return camel_case_to_snake_case(cls.__name__) + "s"
