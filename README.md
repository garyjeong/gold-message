# Gold Message - 금 시세 텔레그램 알림

금값 실시간 시세를 크롤링하여 텔레그램으로 발송하는 프로젝트

## 설정 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 텔레그램 봇 생성
1. 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
2. `/newbot` 명령어로 새 봇 생성
3. 봇 토큰 복사

### 3. Chat ID 확인
1. 생성한 봇과 대화 시작 (아무 메시지나 전송)
2. 브라우저에서 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
3. `chat.id` 값 확인

### 4. 환경 변수 설정
```bash
cp config/.env.example config/.env
```

`config/.env` 파일을 열어 다음 값 입력:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
GOLD_PRICE_URL=https://www.kitco.com/market/
```

## 실행 방법

```bash
cd src
python main.py
```

## 프로젝트 구조

```
gold-message/
├── src/
│   ├── scraper.py       # 금값 크롤링
│   ├── telegram_bot.py  # 텔레그램 발송
│   ├── formatter.py     # 메시지 포맷팅
│   └── main.py          # 메인 실행
├── config/
│   ├── .env             # 환경 변수 (생성 필요)
│   └── .env.example     # 환경 변수 예제
├── requirements.txt     # 의존성
└── README.md
```

## 주의사항

- 크롤링 대상 사이트의 HTML 구조가 변경되면 `scraper.py` 수정 필요
- 과도한 크롤링은 IP 차단 위험이 있으므로 적절한 간격 유지
- `.env` 파일은 절대 공개 저장소에 업로드하지 말 것
