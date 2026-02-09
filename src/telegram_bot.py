import asyncio
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
    
    async def send_message(self, message: str) -> bool:
        """텔레그램으로 메시지 발송"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print("✅ 메시지 발송 성공")
            return True
        except TelegramError as e:
            print(f"❌ 텔레그램 발송 오류: {e}")
            return False
    
    def send_sync(self, message: str) -> bool:
        """동기 방식으로 메시지 발송"""
        return asyncio.run(self.send_message(message))
