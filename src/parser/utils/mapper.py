class Mapper:
    COLUMN_MAPPINGS = {
        "default": {
            "Артикул": "article",
            "Категория": "category",
            "Подкатегория": "subcategory",
            "Код": "code",
            "Товары (работы, услуги)": "product_name",
            "Цена": "price",
            "Количество число": "count",
            "Количество единица": "type_quantity",
        },
        "insert": {
            "Артикул": "article",
            "Код": "code",
            "Категория": "category",
            "Подкатегория": "subcategory",
            "Товары (работы, услуги)": "product_name",
            "Количество число": "count",
            "Количество единица": "type_quantity",
            "Цена": "price",
        },
    }
