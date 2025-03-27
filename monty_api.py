
import requests

from config import Config


class MontyApi:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://resellerapi.montyesim.com/api/v0"
        self.headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
        }
        self._update_access_token()

    def _update_access_token(self):
        self.headers["Access-Token"] = self.get_auth_token()

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

    def get_auth_token(self) -> str:
        body = {
            "username": Config.MONTY_LOGIN,
            "password": Config.MONTY_PASSWORD
        }
        response = self._post("/Agent/login", json=body)
        auth_token = response["access_token"]
        return auth_token

    def get_necessary_bundle_code(self, country: str, gb_amount: str):
        necessary_bundles = []

        region_bundles = self._get(
            f"/Bundles?page_size=100&page_number=1&bundle_category=region&sort_by=price_asc&reseller_admin_view=true"
        )
        for bundle in region_bundles["bundles"]:
            if (bundle["gprs_limit"] == float(gb_amount)
                    and bundle["validity"] == 30
                    and (f"{gb_amount}GB" in bundle["bundle_name"] or f"{float(gb_amount) * 1024}MB")
                    and country.capitalize() in bundle["country_name"]):
                necessary_bundles.append(bundle)

        country_bundles = self._get(
            f"/Bundles?page_size=100&page_number=1&bundle_name={country}&sort_by=price_asc&reseller_admin_view=true"
        )
        for bundle in country_bundles["bundles"]:
            if (bundle["gprs_limit"] == float(gb_amount)
                    and bundle["validity"] == 30
                    and (f"{gb_amount}GB" in bundle["bundle_name"] or f"{float(gb_amount) * 1024}MB")):
                necessary_bundles.append(bundle)

        subscriber_price = ""
        bundle_price = 10000
        bundle_code = ""
        for necessary_bundle in necessary_bundles:
            if bundle_price > necessary_bundle["reseller_retail_price"]:
                bundle_price = necessary_bundle["reseller_retail_price"]
                bundle_code = necessary_bundle["bundle_code"]
                subscriber_price = necessary_bundle["subscriber_price"]
        print(subscriber_price)
        return bundle_code

    def activate_esim(self, bundle_code: str, uuid: str):
        body = {
            "bundle_code": bundle_code,
            "whatsapp_number": "+79774879583",
            "email": "esim.unity@mail.ru",
            "name": "ADmin",
            "order_reference": uuid
        }
        self._post("/Bundles", json=body)

    def get_esim_info(self, uuid: str):
        response = self._get(f"/Orders?order_reference={uuid}")
        return response["orders"][0]

    def get_remaining_data(self, order_id: str):
        response = self._get(f"/Orders/Consumption?order_id={order_id}")
        return response["data_remaining"]


# monty = MontyApi()
# result = monty.get_necessary_bundle_code("japan", "20")
# monty.activate_esim("TUR_0405202408472420", "Z2JWrhoCNXSrMbUntVH6UZW")
# result = monty.get_esim_info("Z2JWrhoCNXSrMbUntVH6UZW")
# print(result)
# print(f"\nLength:{len(result)}")
