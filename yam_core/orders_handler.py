from link_for_marketplace.generate_link_method import generate_links
from yam_core.db_yam import db_get_product_data_by_yam_sku
from yam_core.yam_api import YamApi


def handle_orders():
    # Получаем список новых заказов
    yam_api = YamApi()
    orders_list = yam_api.get_new_orders()

    # Итерируемся по каждому заказу
    for order in orders_list:
        order_id = order["id"]
        items_list = order["items"]

        basket = {"items": []}  # Подготавливаем переменную для сборки тела POST-запроса (далее Корзина)
        # Итерируемся по каждому продукту в заказе
        for item in items_list:
            # Мапим yam_sku на product_data (country и volume)
            yam_sku = item["offerId"]
            product_data = db_get_product_data_by_yam_sku(yam_sku)

            # Генерируем ссылки на товары, получаем их списком
            item_count = item["count"]
            item_links_list = generate_links(item_count, product_data["country"], product_data["volume"], False)

            # Закидываем в Корзину список ссылок активации по каждому товару
            item_id_in_order = item["id"]
            basket["items"].append({
                "id": item_id_in_order,
                "codes": item_links_list,
                "slip": "Инструкция по установке доступна по ссылке: https://telegra.ph/Instrukcii-po-podklyucheniyu-eSIM-12-10",
                "activate_till": "2099-01-01"
            })
        yam_api.send_requested_items(order_id, basket)  # Отправляем заказ клиенту (order_id - номер заказа, basket - тело запроса)


handle_orders()
