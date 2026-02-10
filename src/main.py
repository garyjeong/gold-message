import os
import time
from datetime import datetime
from dotenv import load_dotenv
import schedule
from scraper import GoldPriceScraper
from formatter import MessageFormatter
from telegram_bot import TelegramNotifier


def send_gold_price():
    """금 시세 조회 및 텔레그램 발송"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not all([bot_token, chat_id]):
        print("❌ 환경 변수가 설정되지 않았습니다.")
        return

    print("🔍 금 시세 조회 중...")
    scraper = GoldPriceScraper()
    price_data = scraper.get_price()

    if price_data:
        price_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = MessageFormatter.format_gold_price(price_data)
        print(f"\n📝 발송할 메시지:\n{message}\n")

        notifier = TelegramNotifier(bot_token, chat_id)
        notifier.send_sync(message)
    else:
        print("❌ 금 시세를 가져오지 못했습니다.")


if __name__ == "__main__":
    # 로컬 실행 시 .env 파일 로드 (fly.io에서는 secrets로 주입)
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

    # 매일 오전 8시 (KST) 실행 스케줄 등록
    schedule.every().day.at("08:00").do(send_gold_price)
    print("⏰ 스케줄러 시작 - 매일 08:00 KST 금 시세 알림")

    while True:
        schedule.run_pending()
        time.sleep(30)
