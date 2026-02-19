import os
import json
import logging
from datetime import datetime, time, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from scraper import GoldPriceScraper
from formatter import MessageFormatter

KST = timezone(timedelta(hours=9))
DATA_DIR = Path(__file__).parent.parent / "data"
PRICE_HISTORY_FILE = DATA_DIR / "price_history.json"

logger = logging.getLogger(__name__)


# ── 유틸리티 ─────────────────────────────────────────


def _is_weekend() -> bool:
    """KST 기준 주말(토/일) 여부"""
    return datetime.now(KST).weekday() >= 5


def _fetch_gold_price() -> dict | None:
    """금 시세 조회"""
    scraper = GoldPriceScraper()
    price_data = scraper.get_price()
    if price_data:
        price_data["timestamp"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    return price_data


def _save_daily_price(price_data: dict) -> None:
    """일별 시세를 히스토리 파일에 저장 (주간 리포트용)"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    history = []
    if PRICE_HISTORY_FILE.exists():
        with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    today = datetime.now(KST).strftime("%Y-%m-%d")
    history = [h for h in history if h.get("date") != today]
    history.append({
        "date": today,
        "gold_buy": price_data["gold_buy"],
        "gold_sell": price_data["gold_sell"],
        "gold_pct": price_data["gold_pct"],
        "silver_buy": price_data["silver_buy"],
        "silver_sell": price_data["silver_sell"],
        "silver_pct": price_data["silver_pct"],
        "exchange_rate": price_data["exchange_rate"],
    })

    # 최근 30일만 유지
    history = sorted(history, key=lambda x: x["date"])[-30:]
    with open(PRICE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _get_weekly_history() -> list[dict]:
    """최근 7일간 시세 히스토리 반환"""
    if not PRICE_HISTORY_FILE.exists():
        return []
    with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    cutoff = (datetime.now(KST) - timedelta(days=7)).strftime("%Y-%m-%d")
    return [h for h in history if h["date"] >= cutoff]


# ── 스케줄 콜백 ──────────────────────────────────────


async def scheduled_gold_price(context: ContextTypes.DEFAULT_TYPE) -> None:
    """평일에만 금 시세 발송"""
    if _is_weekend():
        logger.info("주말 - 시세 발송 건너뜀")
        return

    price_data = _fetch_gold_price()
    if price_data:
        _save_daily_price(price_data)
        message = MessageFormatter.format_gold_price(price_data)
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=message,
            parse_mode="HTML",
        )
    else:
        logger.warning("금 시세 조회 실패")


async def scheduled_weekly_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """매주 월요일 주간 요약 리포트 발송"""
    history = _get_weekly_history()
    if not history:
        logger.info("주간 리포트 - 데이터 없음")
        return

    message = MessageFormatter.format_weekly_report(history)
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=message,
        parse_mode="HTML",
    )


# ── 명령어 핸들러 ────────────────────────────────────


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start 명령어 - 봇 안내"""
    message = (
        "🏆 <b>금·은 시세 알림봇</b>\n\n"
        "📋 <b>명령어</b>\n"
        "/gold - 현재 금·은 시세 즉시 조회\n"
        "/weekly - 주간 시세 요약 리포트\n\n"
        "⏰ <b>자동 알림</b>\n"
        "평일 08/11/14/17시 시세 알림\n"
        "매주 월요일 08시 주간 요약 리포트"
    )
    await update.message.reply_text(message, parse_mode="HTML")


async def gold_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/gold 명령어 - 즉시 금 시세 조회"""
    price_data = _fetch_gold_price()
    if price_data:
        _save_daily_price(price_data)
        message = MessageFormatter.format_gold_price(price_data)
    else:
        message = "⚠️ 금 시세를 가져올 수 없습니다. 잠시 후 다시 시도해주세요."
    await update.message.reply_text(message, parse_mode="HTML")


async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/weekly 명령어 - 주간 요약 즉시 조회"""
    history = _get_weekly_history()
    if not history:
        message = "⚠️ 아직 수집된 시세 데이터가 없습니다."
    else:
        message = MessageFormatter.format_weekly_report(history)
    await update.message.reply_text(message, parse_mode="HTML")


# ── 앱 초기화 ────────────────────────────────────────


async def post_init(application: Application) -> None:
    """봇 시작 후 스케줄 작업 등록"""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID 미설정 - 스케줄 알림 비활성화")
        return

    jq = application.job_queue

    # 평일 4회 금 시세 발송 (08:00, 11:00, 14:00, 17:00 KST)
    for hour in [8, 11, 14, 17]:
        jq.run_daily(
            scheduled_gold_price,
            time=time(hour=hour, minute=0, tzinfo=KST),
            chat_id=chat_id,
            name=f"gold_price_{hour:02d}",
        )

    # 매주 월요일 08:00 주간 리포트
    jq.run_daily(
        scheduled_weekly_report,
        time=time(hour=8, minute=0, tzinfo=KST),
        days=(0,),  # Monday
        chat_id=chat_id,
        name="weekly_report",
    )

    logger.info("스케줄러 등록 완료 - 평일 08/11/14/17시 시세, 월요일 08시 주간리포트")


if __name__ == "__main__":
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")

    app = Application.builder().token(bot_token).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("gold", gold_command))
    app.add_handler(CommandHandler("weekly", weekly_command))

    logger.info("금·은 시세 알림봇 시작")
    app.run_polling()
