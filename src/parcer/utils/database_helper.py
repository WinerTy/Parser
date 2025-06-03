from sqlalchemy import create_engine, update, and_
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
import pandas as pd
from sqlalchemy.orm import Session
from models import AutoPart
from core import conf
from utils import Mapper
import logging

from typing import List, Tuple


class DataBaseHelper(Mapper):
    def __init__(self, url: str):
        self.engine = create_engine(url)
        self.logger = logging.getLogger(__name__)

    def _prepare_data(
        self, df: pd.DataFrame, mapping_type: str = "default"
    ) -> pd.DataFrame:
        """Подготовка данных: переименование и фильтрация колонок"""
        mappings = self.COLUMN_MAPPINGS.get(mapping_type, {})
        return df.rename(columns=mappings).drop(columns=["Сумма", "№"], errors="ignore")

    def get_actual_data(self, table_name: str = "auto_parts") -> pd.DataFrame:
        """Получение текущих данных из таблицы"""
        try:
            return pd.read_sql_table(table_name, self.engine)
        except NoSuchTableError:
            self.logger.warning(
                f"Table {table_name} not found, returning empty DataFrame"
            )
            return pd.DataFrame()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting data from {table_name}: {e}")
            raise

    def update_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Обновление данных в БД с управлением is_active
        Возвращает:
        - Обновленный DataFrame
        - Список ненайденных артикулов
        """
        session = None  # Инициализируем переменную session
        try:
            # Подготовка данных
            db_data = self.get_actual_data().drop(columns=["id"])
            file_data = self._prepare_data(df)

            # Получаем артикулы из файла
            file_articles = set(file_data["article"].unique())

            # Создаем словарь с данными для обновления (артикул -> (count, price))
            updates = {
                row["article"]: (row["count"], row["price"])
                for _, row in file_data.iterrows()
            }

            not_found = []

            # Обновление DataFrame
            db_data["count"] = (
                db_data["article"]
                .map(lambda x: updates.get(x, (None, None))[0])
                .fillna(db_data["count"])
                .astype("int32")
            )
            db_data["price"] = (
                db_data["article"]
                .map(lambda x: updates.get(x, (None, None))[1])
                .fillna(db_data["price"])
                .astype("float32")
            )

            # Обновление БД
            session = Session(self.engine)

            # 1. Получаем все существующие артикулы
            existing_articles = {a[0] for a in session.query(AutoPart.article).all()}

            # 2. Обновляем записи из файла (активные)
            for article, (count, price) in updates.items():
                if article not in existing_articles:
                    not_found.append(article)
                    continue

                stmt = (
                    update(AutoPart)
                    .where(AutoPart.article == article)
                    .values(
                        count=count,
                        price=price,
                        is_active=True,
                    )
                )
                session.execute(stmt)

            # 3. Деактивируем записи, которых нет в файле
            if file_articles:
                deactivate_stmt = (
                    update(AutoPart)
                    .where(
                        and_(
                            AutoPart.article.notin_(file_articles),
                            AutoPart.is_active,
                        )
                    )
                    .values(is_active=False)
                )
                session.execute(deactivate_stmt)

            session.commit()

            if not_found:
                self.logger.warning(f"Articles not found: {not_found}")

            return db_data, not_found

        except Exception as e:
            self.logger.error(f"Update error: {e}")
            if session:
                session.rollback()
            raise
        finally:
            if session:
                session.close()

    def insert_new_data(
        self,
        file_path: str,
        table_name: str = "auto_parts",
        override: bool = False,
        batch_size: int = 1000,
    ) -> Tuple[int, int, int]:
        """
        Вставка новых данных с автоматической активацией
        Возвращает:
        - Количество добавленных записей
        - Количество обновленных записей
        - Количество деактивированных записей
        """
        try:
            new_data = self._prepare_data(pd.read_excel(file_path), "insert")
            records = new_data.to_dict(orient="records")
            file_articles = {r["article"] for r in records}

            added, updated, deactivated = 0, 0, 0

            with Session(self.engine) as session:
                # 1. Получаем все артикулы
                existing_parts = session.query(AutoPart).all()
                existing_articles = {part.article for part in existing_parts}

                # 2. Обработка новых данных
                for i in range(0, len(records), batch_size):
                    batch = records[i : i + batch_size]
                    batch_add = []

                    for item in batch:
                        if item["article"] in existing_articles:
                            if override:
                                part = (
                                    session.query(AutoPart)
                                    .filter_by(article=item["article"])
                                    .first()
                                )
                                for k, v in item.items():
                                    setattr(part, k, v)
                                part.is_active = True
                                updated += 1
                        else:
                            batch_add.append(AutoPart(**item, is_active=True))
                            added += 1

                    if batch_add:
                        session.bulk_save_objects(batch_add)

                # 3. Деактивация отсутствующих товаров
                if file_articles:
                    deactivated = (
                        session.query(AutoPart)
                        .filter(
                            and_(
                                AutoPart.article.notin_(file_articles),
                                AutoPart.is_active,
                            )
                        )
                        .update(
                            {"is_active": False},
                            synchronize_session=False,
                        )
                    )

                session.commit()

            self.logger.info(
                f"Added: {added}, Updated: {updated}, Deactivated: {deactivated}"
            )
            return added, updated, deactivated

        except Exception as e:
            self.logger.error(f"Insert error: {e}")
            session.rollback()
            raise


db_helper = DataBaseHelper(url=conf.db.url)
