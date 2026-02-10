import requests
from datetime import date, timedelta
from typing import Optional, Dict, Tuple

# 단위 환산 상수
GRAM_PER_DON = 3.75
TROY_OZ_TO_GRAM = 31.1034768

# 금은방 마진율 (기준시세 대비)
BUY_MARGIN = 0.15    # 살 때: +15% (부가세 10% + 공임 약 5%)
SELL_MARGIN = 0.045  # 팔 때: -4.5% (감정수수료)


class GoldPriceScraper:
    def __init__(self):
        self.api_url = "https://data-asg.goldprice.org/dbXRates/USD"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; GoldBot/1.0)",
        }

    def _prev_business_day(self, d: date) -> date:
        """직전 영업일 반환 (주말 건너뛰기)"""
        prev = d - timedelta(days=1)
        while prev.weekday() >= 5:
            prev -= timedelta(days=1)
        return prev

    def get_exchange_rates(self) -> Tuple[float, float]:
        """USD/KRW 현재 환율 + 전일 환율 조회 (frankfurter.app)"""
        try:
            # 최신 환율
            r = requests.get(
                "https://api.frankfurter.app/latest",
                params={"from": "USD", "to": "KRW"},
                headers=self.headers, timeout=10,
            )
            latest = r.json()
            current_rate = latest["rates"]["KRW"]
            latest_date = date.fromisoformat(latest["date"])

            # 직전 영업일 환율
            prev_date = self._prev_business_day(latest_date)
            r = requests.get(
                f"https://api.frankfurter.app/{prev_date}",
                params={"from": "USD", "to": "KRW"},
                headers=self.headers, timeout=10,
            )
            prev_rate = r.json()["rates"]["KRW"]

            return current_rate, prev_rate
        except Exception:
            return 1400.0, 1400.0

    def _usd_oz_to_krw_don(self, usd_per_oz: float, exchange_rate: float) -> float:
        """USD/트로이온스 → KRW/돈 환산"""
        return (usd_per_oz / TROY_OZ_TO_GRAM) * exchange_rate * GRAM_PER_DON

    def get_price(self) -> Optional[Dict]:
        """금·은 1돈 기준 금은방 매매가격 반환"""
        try:
            response = requests.get(
                self.api_url, headers=self.headers, timeout=10
            )
            response.raise_for_status()
            item = response.json()["items"][0]
        except Exception as e:
            print(f"시세 조회 오류: {e}")
            return None

        exchange_rate, prev_exchange_rate = self.get_exchange_rates()

        # 금 (XAU)
        gold_base = self._usd_oz_to_krw_don(item["xauPrice"], exchange_rate)
        gold_prev = self._usd_oz_to_krw_don(item["xauClose"], exchange_rate)

        # 은 (XAG)
        silver_base = self._usd_oz_to_krw_don(item["xagPrice"], exchange_rate)
        silver_prev = self._usd_oz_to_krw_don(item["xagClose"], exchange_rate)

        # 환율 전일대비
        fx_diff = exchange_rate - prev_exchange_rate
        fx_pct = (fx_diff / prev_exchange_rate) * 100 if prev_exchange_rate else 0

        return {
            "gold_buy": gold_base * (1 + BUY_MARGIN),
            "gold_sell": gold_base * (1 - SELL_MARGIN),
            "gold_diff": gold_base - gold_prev,
            "gold_pct": item["pcXau"],
            "silver_buy": silver_base * (1 + BUY_MARGIN),
            "silver_sell": silver_base * (1 - SELL_MARGIN),
            "silver_diff": silver_base - silver_prev,
            "silver_pct": item["pcXag"],
            "exchange_rate": exchange_rate,
            "fx_diff": fx_diff,
            "fx_pct": fx_pct,
        }
