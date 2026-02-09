import requests
from typing import Optional, Dict

# 1돈 = 3.75g
GRAM_PER_DON = 3.75


class GoldPriceScraper:
    def __init__(self, service_key: str):
        self.service_key = service_key
        self.api_url = (
            "https://apis.data.go.kr/1160100/service/"
            "GetGeneralProductInfoService/getGoldPriceInfo"
        )

    def get_usd_to_krw_rate(self) -> float:
        """USD/KRW 환율 조회"""
        try:
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/USD", timeout=10
            )
            data = response.json()
            return data["rates"].get("KRW", 1400.0)
        except Exception:
            return 1400.0

    def fetch_gold_price(self) -> Optional[Dict]:
        """공공데이터포털 API에서 KRX 금 시세 조회 (금 99.99_1kg 기준)"""
        try:
            params = {
                "serviceKey": self.service_key,
                "resultType": "json",
                "numOfRows": 2,
                "pageNo": 1,
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data["response"]["body"]["items"]["item"]

            # 금 99.99_1kg 종목 찾기
            for item in items:
                if item["itmsNm"] == "금 99.99_1kg":
                    return item

            return None
        except Exception as e:
            print(f"API 조회 오류: {e}")
            return None

    def get_price(self) -> Optional[Dict]:
        """금 1돈 기준 시세 데이터 반환"""
        item = self.fetch_gold_price()
        if not item:
            return None

        exchange_rate = self.get_usd_to_krw_rate()

        # KRX 금 시세는 1g 기준 가격
        price_per_gram = int(item["clpr"])
        vs_per_gram = int(item["vs"])

        # 1돈(3.75g) 기준으로 환산
        price_krw = price_per_gram * GRAM_PER_DON
        vs_krw = vs_per_gram * GRAM_PER_DON
        price_usd = price_krw / exchange_rate

        return {
            "price_krw": price_krw,
            "price_usd": price_usd,
            "vs": vs_krw,
            "flt_rt": float(item["fltRt"]),
            "bas_dt": item["basDt"],
            "exchange_rate": exchange_rate,
        }
