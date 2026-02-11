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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; GoldBot/1.0)",
        }

    def _prev_business_day(self, d: date) -> date:
        """직전 영업일 반환 (주말 건너뛰기)"""
        prev = d - timedelta(days=1)
        while prev.weekday() >= 5:
            prev -= timedelta(days=1)
        return prev

    # ── 금/은 시세 ──────────────────────────────────────

    def _get_realtime_prices(self) -> Optional[Dict]:
        """gold-api.com 실시간 금/은 현재가 (USD/oz)"""
        try:
            gold = requests.get(
                "https://api.gold-api.com/price/XAU",
                headers=self.headers, timeout=10,
            ).json()
            silver = requests.get(
                "https://api.gold-api.com/price/XAG",
                headers=self.headers, timeout=10,
            ).json()
            return {
                "xauPrice": gold["price"],
                "xagPrice": silver["price"],
            }
        except Exception as e:
            print(f"gold-api.com 조회 실패: {e}")
            return None

    def _get_close_data(self) -> Optional[Dict]:
        """goldprice.org 전일 종가 + 변동률"""
        try:
            r = requests.get(
                "https://data-asg.goldprice.org/dbXRates/USD",
                headers=self.headers, timeout=10,
            )
            r.raise_for_status()
            item = r.json()["items"][0]
            return {
                "xauPrice": item["xauPrice"],
                "xagPrice": item["xagPrice"],
                "xauClose": item["xauClose"],
                "xagClose": item["xagClose"],
                "pcXau": item["pcXau"],
                "pcXag": item["pcXag"],
            }
        except Exception as e:
            print(f"goldprice.org 조회 실패: {e}")
            return None

    # ── 환율 ────────────────────────────────────────────

    def _get_rate_open_er(self) -> Optional[float]:
        """open.er-api.com 현재 환율"""
        try:
            r = requests.get(
                "https://open.er-api.com/v6/latest/USD",
                headers=self.headers, timeout=10,
            )
            return r.json()["rates"]["KRW"]
        except Exception:
            return None

    def _get_rate_fawazahmed(self, d: Optional[date] = None) -> Optional[float]:
        """fawazahmed0/currency-api 환율 (날짜 지정 가능)"""
        try:
            if d:
                url = (
                    f"https://cdn.jsdelivr.net/npm/"
                    f"@fawazahmed0/currency-api@{d}/v1/currencies/usd.json"
                )
            else:
                url = (
                    "https://cdn.jsdelivr.net/npm/"
                    "@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
                )
            r = requests.get(url, headers=self.headers, timeout=10)
            return r.json()["usd"]["krw"]
        except Exception:
            return None

    def get_exchange_rates(self) -> Tuple[float, float]:
        """USD/KRW 현재 환율 + 전일 환율 조회"""
        # 현재 환율: open.er-api.com → fawazahmed0 → 기본값
        current_rate = self._get_rate_open_er()
        if current_rate is None:
            current_rate = self._get_rate_fawazahmed()
        if current_rate is None:
            print("환율 조회 실패: 기본값 사용")
            return 1400.0, 1400.0

        # 전일 환율: fawazahmed0 과거 날짜 조회
        today = date.today()
        prev_date = self._prev_business_day(today)
        prev_rate = self._get_rate_fawazahmed(prev_date)
        if prev_rate is None:
            prev_rate = current_rate

        return current_rate, prev_rate

    # ── 통합 조회 ───────────────────────────────────────

    def _usd_oz_to_krw(self, usd_per_oz: float, exchange_rate: float) -> float:
        """USD/트로이온스 → KRW/g 환산"""
        return (usd_per_oz / TROY_OZ_TO_GRAM) * exchange_rate

    def get_price(self) -> Optional[Dict]:
        """금(1돈)·은(1g) 기준 금은방 매매가격 반환"""
        # 실시간 현재가 (gold-api.com)
        realtime = self._get_realtime_prices()

        # 전일 종가/변동률 (goldprice.org)
        close_data = self._get_close_data()

        # 현재가 결정: gold-api.com → goldprice.org
        if realtime:
            xau_now = realtime["xauPrice"]
            xag_now = realtime["xagPrice"]
        elif close_data:
            xau_now = close_data["xauPrice"]
            xag_now = close_data["xagPrice"]
        else:
            print("금/은 시세 조회 실패: 모든 소스 불가")
            return None

        # 전일종가: goldprice.org → 없으면 현재가로 대체 (변동 0)
        xau_close = close_data["xauClose"] if close_data else xau_now
        xag_close = close_data["xagClose"] if close_data else xag_now
        pc_xau = close_data["pcXau"] if close_data else 0.0
        pc_xag = close_data["pcXag"] if close_data else 0.0

        exchange_rate, prev_exchange_rate = self.get_exchange_rates()

        # 금 (XAU) - 1돈(3.75g) 기준
        gold_base = self._usd_oz_to_krw(xau_now, exchange_rate) * GRAM_PER_DON
        gold_prev = self._usd_oz_to_krw(xau_close, exchange_rate) * GRAM_PER_DON

        # 은 (XAG) - 1g 기준
        silver_base = self._usd_oz_to_krw(xag_now, exchange_rate)
        silver_prev = self._usd_oz_to_krw(xag_close, exchange_rate)

        # 환율 전일대비
        fx_diff = exchange_rate - prev_exchange_rate
        fx_pct = (fx_diff / prev_exchange_rate) * 100 if prev_exchange_rate else 0

        return {
            "gold_buy": gold_base * (1 + BUY_MARGIN),
            "gold_sell": gold_base * (1 - SELL_MARGIN),
            "gold_diff": gold_base - gold_prev,
            "gold_pct": pc_xau,
            "silver_buy": silver_base * (1 + BUY_MARGIN),
            "silver_sell": silver_base * (1 - SELL_MARGIN),
            "silver_diff": silver_base - silver_prev,
            "silver_pct": pc_xag,
            "exchange_rate": exchange_rate,
            "fx_diff": fx_diff,
            "fx_pct": fx_pct,
        }
