import requests

from config import Config


class YamApi:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {"accept": "application/json", "Api-Key": Config.YAM_API_KEY}
        self.base_url = "https://api.partner.market.yandex.ru"
        self.campaign_id = Config.YAM_CAMPAIGN_ID

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, verify=False, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {e}")
            return {}

    def _get(self, path: str, **kwargs) -> dict:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> dict:
        return self._request("POST", path, **kwargs)

    def get_new_orders(self):
        return self._get(f"//campaigns/{self.campaign_id}/orders?fake=true&status=PROCESSING")["orders"]

    def send_requested_items(self, order_id, body):
        return self._post(f"/campaigns/{self.campaign_id}/orders/{order_id}/deliverDigitalGoods", json=body)
