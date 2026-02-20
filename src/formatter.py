from typing import Dict, List


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
            f"🏆 금·은 시세\n"
            f"\n"
            f"[ 금 · 1돈(3.75g) ]\n"
            f"🏪 살 때: {data['gold_buy']:,.0f}원\n"
            f"💰 팔 때: {data['gold_sell']:,.0f}원\n"
            f"{cls._arrow(data['gold_diff'])} 전일대비: {gd}원 ({gp}%)\n"
            f"\n"
            f"[ 은 · 1g ]\n"
            f"🏪 살 때: {data['silver_buy']:,.0f}원\n"
            f"💰 팔 때: {data['silver_sell']:,.0f}원\n"
            f"{cls._arrow(data['silver_diff'])} 전일대비: {sd}원 ({sp}%)\n"
            f"\n"
            f"💱 환율: {data['exchange_rate']:,.2f} KRW/USD"
            f" ({cls._signed(data['fx_diff'], '.2f')}원,"
            f" {cls._signed(data['fx_pct'], '.2f')}%)\n"
            f"⏰ 조회: {data.get('timestamp', 'N/A')}\n"
            f"\n"
            f'📈 <a href="https://kr.investing.com/commodities/gold">금 차트</a>'
            f' | <a href="https://kr.investing.com/commodities/silver">은 차트</a>'
        )

        return message

    @classmethod
    def format_weekly_report(cls, history: List[Dict]) -> str:
        """최근 7일간 시세 히스토리를 주간 요약 메시지로 변환"""
        if not history:
            return "⚠️ 주간 시세 데이터가 없습니다."

        latest = history[-1]
        oldest = history[0]

        gold_buy_start = oldest["gold_buy"]
        gold_buy_end = latest["gold_buy"]
        gold_week_diff = gold_buy_end - gold_buy_start
        gold_week_pct = (gold_week_diff / gold_buy_start) * 100 if gold_buy_start else 0

        silver_buy_start = oldest["silver_buy"]
        silver_buy_end = latest["silver_buy"]
        silver_week_diff = silver_buy_end - silver_buy_start
        silver_week_pct = (silver_week_diff / silver_buy_start) * 100 if silver_buy_start else 0

        fx_start = oldest["exchange_rate"]
        fx_end = latest["exchange_rate"]
        fx_week_diff = fx_end - fx_start
        fx_week_pct = (fx_week_diff / fx_start) * 100 if fx_start else 0

        gold_high = max(h["gold_buy"] for h in history)
        gold_low = min(h["gold_buy"] for h in history)
        silver_high = max(h["silver_buy"] for h in history)
        silver_low = min(h["silver_buy"] for h in history)

        period = f"{oldest['date']} ~ {latest['date']}"

        lines = [
            f"📊 주간 시세 요약",
            f"📅 {period} ({len(history)}일간)",
            f"",
            f"[ 금 · 1돈(3.75g) ]",
            f"🏪 현재 살 때: {gold_buy_end:,.0f}원",
            f"{cls._arrow(gold_week_diff)} 주간 변동: {cls._signed(gold_week_diff, ',.0f')}원 ({cls._signed(gold_week_pct, '.2f')}%)",
            f"📈 최고: {gold_high:,.0f}원 / 최저: {gold_low:,.0f}원",
            f"",
            f"[ 은 · 1g ]",
            f"🏪 현재 살 때: {silver_buy_end:,.0f}원",
            f"{cls._arrow(silver_week_diff)} 주간 변동: {cls._signed(silver_week_diff, ',.0f')}원 ({cls._signed(silver_week_pct, '.2f')}%)",
            f"📈 최고: {silver_high:,.0f}원 / 최저: {silver_low:,.0f}원",
            f"",
            f"💱 환율: {fx_end:,.2f} KRW/USD ({cls._signed(fx_week_diff, '.2f')}원, {cls._signed(fx_week_pct, '.2f')}%)",
        ]

        # 일별 추이
        lines.append(f"")
        lines.append(f"[ 일별 금 시세 추이 ]")
        for h in history:
            arrow = cls._arrow(h.get("gold_pct", 0))
            pct = cls._signed(h.get("gold_pct", 0), ".2f")
            lines.append(f"{h['date'][-5:]}  {h['gold_buy']:>10,.0f}원 {arrow}{pct}%")

        return "\n".join(lines)
