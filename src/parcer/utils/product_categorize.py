import pandas as pd

import numpy as np

from .exsel_parser import ExcelParser
from typing import Optional

from matcher import CategoryMatcher
from rules import category_rule
from utils.database_helper import db_helper


class ProductManager(ExcelParser):
    MAIN_QUANTITY_COL_NAME: str = "Количество"
    NUMERIC_QUANTITY_COL_NAME: str = "Количество число"
    UNIT_QUANTITY_COL_NAME: str = "Количество единица"

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.matcher = CategoryMatcher(category_rule)
        self.db_helper = db_helper
        self.df: Optional[pd.DataFrame] = None  # Инициализируем df как None
        self._init_dataframe()  # Загружаем DataFrame

    def _init_dataframe(self):
        if self.start_row > 0:
            rows_to_skip = self.start_row - 1
            try:
                self.df = pd.read_excel(self.path, skiprows=rows_to_skip, header=0)
                if self.end_row > 0 and self.end_row < self.sheet.max_row:
                    last_data_row_in_df = self.end_row - (
                        rows_to_skip + 1
                    )  # +1 for header row itself
                    if 0 <= last_data_row_in_df < len(self.df):
                        self.df = self.df.iloc[: last_data_row_in_df + 1]

            except Exception:
                raise

    def _handle_quantity_columns(self) -> None:
        """
        Находит колонку 'Количество' и следующую за ней 'Unnamed: X',
        переименовывает их в 'Количество_число' и 'Количество_единица'.
        """
        if self.df is None:
            return

        try:
            # Ищем индекс колонки, которая получила имя из объединенной ячейки
            qty_col_idx = self.df.columns.get_loc(self.MAIN_QUANTITY_COL_NAME)
            print(qty_col_idx)
            # Следующая колонка (с единицами измерения) должна быть 'Unnamed: X'
            # Ее реальный индекс в df.columns будет qty_col_idx + 1
            if qty_col_idx + 4 < len(self.df.columns):
                unit_col_original_name = self.df.columns[qty_col_idx + 4]
                # Проверка, что это действительно "Unnamed" колонка, чтобы не переименовать что-то важное
                if (
                    isinstance(unit_col_original_name, str)
                    and "Unnamed" in unit_col_original_name
                ):
                    rename_map = {
                        self.MAIN_QUANTITY_COL_NAME: self.NUMERIC_QUANTITY_COL_NAME,
                        unit_col_original_name: self.UNIT_QUANTITY_COL_NAME,
                    }
                    self.df.rename(columns=rename_map, inplace=True)
                else:
                    print(
                        f"Предупреждение: Колонка '{unit_col_original_name}' после '{self.MAIN_QUANTITY_COL_NAME}' не является 'Unnamed'. Единицы измерения могут быть не обработаны."
                    )
                    # Можно просто переименовать первую часть, если второй нет или она не Unnamed
                    self.df.rename(
                        columns={
                            self.MAIN_QUANTITY_COL_NAME: self.NUMERIC_QUANTITY_COL_NAME
                        },
                        inplace=True,
                    )
            else:
                # Если нет следующей колонки, просто переименовываем основную
                self.df.rename(
                    columns={
                        self.MAIN_QUANTITY_COL_NAME: self.NUMERIC_QUANTITY_COL_NAME
                    },
                    inplace=True,
                )
                print(
                    f"Предупреждение: Нет колонки после '{self.MAIN_QUANTITY_COL_NAME}'. Только она переименована в '{self.NUMERIC_QUANTITY_COL_NAME}'."
                )

        except KeyError:
            print(
                f"Предупреждение: Основная колонка количества '{self.MAIN_QUANTITY_COL_NAME}' не найдена."
            )
        except Exception as e:
            print(f"Ошибка при обработке колонок количества: {e}")

    def process_data(self) -> pd.DataFrame:
        """Выполняет все шаги обработки DataFrame."""
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        self._handle_quantity_columns()
        self._delete_unnecessary_unnamed_columns()
        self._add_category_columns()
        self._delete_duplicate_headers()
        self._drop_all_na_rows()
        return self.df.copy()

    def _delete_unnecessary_unnamed_columns(self) -> None:
        """Удаляет колонки 'Unnamed: X'."""
        if self.df is None:
            return
        cols_for_drop = []
        for col in self.df.columns:
            col_name = str(col)
            if col_name.startswith("Unnamed"):
                cols_for_drop.append(col_name)

        if cols_for_drop:
            self.df.drop(columns=cols_for_drop, inplace=True)

    def _add_category_columns(self) -> None:
        """Добавляет колонки 'Категория' и 'Подкатегория'."""
        if self.df is None:
            return
        target_col = "Артикул"
        try:
            idx = self.df.columns.get_loc(target_col)
            if "Категория" not in self.df.columns:
                self.df.insert(loc=idx + 1, column="Категория", value=np.nan)
            if "Подкатегория" not in self.df.columns:
                self.df.insert(loc=idx + 2, column="Подкатегория", value=np.nan)
        except KeyError:
            print(
                f"Предупреждение: Колонка '{target_col}' не найдена. Колонки категорий не добавлены."
            )
        except Exception as e:
            print(f"Ошибка при добавлении колонок категорий: {e}")

    def _delete_duplicate_headers(self) -> None:
        """Удаляет строки, которые являются дубликатами заголовков."""
        if self.df is None:
            return
        if "№" in self.df.columns:
            # Ищем строки, где в колонке "№" стоит значение "№" (это дубликаты заголовков)
            duplicate_header_indices = self.df[self.df["№"] == "№"].index
            if not duplicate_header_indices.empty:
                self.df.drop(axis=0, index=duplicate_header_indices, inplace=True)
                print(
                    f"Удалены дубликаты строк заголовков: {len(duplicate_header_indices)} строк."
                )
        else:
            print(
                "Предупреждение: Колонка '№' не найдена, дубликаты заголовков не удалены."
            )

    def _drop_all_na_rows(self) -> None:
        """Удаляет строки, где все значения NaN."""
        if self.df is None:
            return
        self.df.dropna(axis=0, how="all", inplace=True)

    def to_excel(self):
        self.process_data()
        actual_data = self.db_helper.get_actual_data()
        actual_data = actual_data.rename(
            columns={
                "article": "Артикул",
                "category": "Категория",
                "subcategory": "Подкатегория",
                "code": "Код",
                "name": "Название",
                "product_name": "Товары (работы, услуги)",
                "price": "Цена",
                "count": self.NUMERIC_QUANTITY_COL_NAME,
                "type_quantity": self.UNIT_QUANTITY_COL_NAME,
            }
        )

        # Convert columns to appropriate types before updating
        actual_data["Категория"] = actual_data["Категория"].astype(object)
        actual_data["Подкатегория"] = actual_data["Подкатегория"].astype(object)

        actual_data = actual_data.set_index("Артикул")
        self.df = self.df.set_index("Артикул")

        # Ensure target columns in self.df are also object type for string compatibility
        for col in ["Категория", "Подкатегория"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(object)

        self.df.update(
            actual_data[
                [
                    "Категория",
                    "Подкатегория",
                    self.NUMERIC_QUANTITY_COL_NAME,
                    self.UNIT_QUANTITY_COL_NAME,
                    "Цена",
                ]
            ]
        )
        self.df[["Категория", "Подкатегория"]] = self.df[
            "Товары (работы, услуги)"
        ].apply(lambda name: pd.Series(self.matcher.find_category(name)))
        self.df = self.df.reset_index()
        self.df.to_excel(self.path, index=False)

    def find_empty_category(self):
        return (self.df[self.df["Категория"] == "Не определено"].index + 2).tolist()
