from typing import Dict


class MessageFormatter:
    @staticmethod
    def format_gold_price(data: Dict) -> str:
        """금 1돈 기준 시세 데이터를 텔레그램 메시지 형식으로 변환"""
        if not data:
            return "⚠️ 금 시세 정보를 가져올 수 없습니다."

        # 기준일자 포맷
        dt = data["bas_dt"]
        bas_dt_fmt = f"{dt[:4]}-{dt[4:6]}-{dt[6:]}"

        # 전일대비 부호
        vs = data["vs"]
        vs_sign = "+" if vs > 0 else ""
        flt_rt = data["flt_rt"]
        rt_sign = "+" if flt_rt > 0 else ""

        # 등락 아이콘
        if vs > 0:
            arrow = "🔺"
        elif vs < 0:
            arrow = "🔻"
        else:
            arrow = "➖"

        message = (
            f"🏆 금 시세 (1돈 기준)\n"
            f"📅 {bas_dt_fmt}\n"
            f"\n"
            f"💵 현재시세(USD): ${data['price_usd']:,.2f}\n"
            f"💰 현재시세(KRW): {data['price_krw']:,.0f}원\n"
            f"{arrow} 전일대비: {vs_sign}{vs:,.0f}원\n"
            f"📊 등락률: {rt_sign}{flt_rt}%\n"
            f"\n"
            f"💱 적용환율: {data['exchange_rate']:,.2f} KRW/USD\n"
            f"⏰ 조회: {data.get('timestamp', 'N/A')}"
        )

        return message
