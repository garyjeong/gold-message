from typing import Dict


class MessageFormatter:
    @staticmethod
    def _arrow(value: float) -> str:
        if value > 0:
            return "🔺"
        elif value < 0:
            return "🔻"
        return "➖"

    @staticmethod
    def _signed(value: float, fmt: str) -> str:
        sign = "+" if value > 0 else ""
        return f"{sign}{value:{fmt}}"

    @classmethod
    def format_gold_price(cls, data: Dict) -> str:
        """금·은 1돈 기준 금은방 매매가격을 텔레그램 메시지 형식으로 변환"""
        if not data:
            return "⚠️ 시세 정보를 가져올 수 없습니다."

        gd = cls._signed(data["gold_diff"], ",.0f")
        gp = cls._signed(data["gold_pct"], ".2f")
        sd = cls._signed(data["silver_diff"], ",.0f")
        sp = cls._signed(data["silver_pct"], ".2f")

        message = (
            f"🏆 금·은 시세 (1돈 기준)\n"
            f"\n"
            f"🏪 금은방 살 때(금): {data['gold_buy']:,.0f}원\n"
            f"💰 금은방 팔 때(금): {data['gold_sell']:,.0f}원\n"
            f"{cls._arrow(data['gold_diff'])} 전일대비(금): {gd}원 ({gp}%)\n"
            f"\n"
            f"🏪 금은방 살 때(은): {data['silver_buy']:,.0f}원\n"
            f"💰 금은방 팔 때(은): {data['silver_sell']:,.0f}원\n"
            f"{cls._arrow(data['silver_diff'])} 전일대비(은): {sd}원 ({sp}%)\n"
            f"\n"
            f"💱 환율: {data['exchange_rate']:,.2f} KRW/USD"
            f" ({cls._signed(data['fx_diff'], '.2f')}원,"
            f" {cls._signed(data['fx_pct'], '.2f')}%)\n"
            f"⏰ 조회: {data.get('timestamp', 'N/A')}"
        )

        return message
