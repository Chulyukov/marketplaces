from db.db_connection import execute_query


def db_get_product_data_by_yam_sku(yam_sku):
    """Получаем данные по продукту bnesim по yam_sku"""
    result = execute_query(
        "Ошибка при получении данных по продукту bnesim по yam_sku",
        "SELECT country, volume FROM bnesim_products WHERE yam_sku=%s",
        (yam_sku,)
    )
    return {"country": result[0][0], "volume": result[0][1]} if result else None


info = db_get_product_data_by_yam_sku("MRKT-MI9CRI4N")
print(info["country"])
print(info["volume"])