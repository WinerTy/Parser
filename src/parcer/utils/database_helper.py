from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchTableError
import pandas as pd
from sqlalchemy.orm import Session
from models import AutoPart
from core import conf


class DataBaseHelper:
    def __init__(self, url: str):
        self.engine = create_engine(url)

    def get_actual_data(self, table_name: str = "auto_parts"):
        try:
            with self.engine.connect() as session:
                return pd.read_sql_table(table_name, session)
        except NoSuchTableError:
            return pd.DataFrame()

    def insert_new_data(
        self, file_path: str, table_name: str = "auto_parts", override: bool = False
    ):
        # Чтение и подготовка новых данных
        new_data = pd.read_excel(file_path)
        mapper_cols = {
            "Артикул": "article",
            "Код": "code",
            "Категория": "category",
            "Подкатегория": "subcategory",
            "Товары (работы, услуги)": "product_name",
            "Количество число": "count",
            "Количество единица": "type_quantity",
            "Цена": "price",
        }
        new_data = new_data.rename(columns=mapper_cols).drop(columns=["Сумма", "№"])
        new_records = new_data.to_dict(orient="records")

        with Session(self.engine) as session:
            # Получаем все существующие записи одним запросом
            existing_parts = session.query(AutoPart).all()
            existing_articles = {part.article: part for part in existing_parts}

            # Подготовка списков для bulk операций
            to_update = []
            to_add = []

            for item in new_records:
                article = item["article"]
                if article in existing_articles:
                    if override:
                        existing = existing_articles[article]
                        # Обновляем только измененные поля
                        for key, value in item.items():
                            if getattr(existing, key) != value:
                                setattr(existing, key, value)
                        # Добавляем в список только если есть изменения
                        if existing in session.dirty:
                            to_update.append(existing)
                else:
                    to_add.append(AutoPart(**item))

            # Массовые операции
            if to_update:
                session.bulk_save_objects(to_update, update_changed_only=True)
            if to_add:
                session.bulk_save_objects(to_add)
            session.commit()


db_helper = DataBaseHelper(url=conf.db.url)
