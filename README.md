# Gold Message - 금 시세 텔레그램 알림

금값 실시간 시세를 크롤링하여 텔레그램으로 발송하는 프로젝트

## 기능

- Kitco.com에서 국제 금 시세 크롤링
- USD/KRW 환율 자동 조회
- 그램당 가격으로 환산 (USD, KRW)
- 텔레그램 봇을 통한 실시간 알림

## 설정 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

필요한 패키지:
- `requests` - HTTP 요청
- `beautifulsoup4` - HTML 파싱
- `python-telegram-bot` - 텔레그램 API
- `python-dotenv` - 환경 변수 관리

### 2. 텔레그램 봇 생성
1. 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
2. `/newbot` 명령어로 새 봇 생성
3. 봇 이름과 username 설정
4. 받은 봇 토큰 복사

### 3. Chat ID 확인
1. 생성한 봇과 대화 시작 (아무 메시지나 전송)
2. 브라우저에서 다음 URL 접속:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. 응답 JSON에서 `"chat":{"id":숫자}` 부분의 숫자 확인

### 4. 환경 변수 설정
```bash
cp config/.env.example config/.env
```

`config/.env` 파일을 열어 다음 값 입력:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
GOLD_PRICE_URL=https://www.kitco.com/market/
```

## 실행 방법

```bash
cd src
python3 main.py
```

## 메시지 형식

```
🏆 금 시세 정보

📊 전일 대비: 27.10(0.55%)
💰 현재가: $160.53/g
🇰🇷 원화: 235,019원/g
💱 환율: 1,464.00 KRW/USD

⏰ 조회 시간: 2026-02-09 11:15:00
```

## 프로젝트 구조

```
gold-message/
├── src/
│   ├── scraper.py       # 금값 크롤링 및 환율 조회
│   ├── telegram_bot.py  # 텔레그램 발송
│   ├── formatter.py     # 메시지 포맷팅
│   └── main.py          # 메인 실행
├── config/
│   ├── .env             # 환경 변수 (생성 필요)
│   └── .env.example     # 환경 변수 예제
├── requirements.txt     # 의존성
├── .gitignore          # Git 제외 파일
└── README.md
```

## 주요 기능 설명

### scraper.py
- Kitco.com에서 금 시세 크롤링
- exchangerate-api.com에서 USD/KRW 환율 조회
- 온스(oz)당 가격을 그램(g)당 가격으로 환산
  - 1 트로이 온스 = 31.1034768 그램

### telegram_bot.py
- python-telegram-bot 라이브러리 사용
- 비동기 메시지 발송 지원

### formatter.py
- 금 시세 데이터를 보기 좋은 형식으로 변환
- 이모지를 활용한 가독성 향상

## 주의사항

- 크롤링 대상 사이트의 HTML 구조가 변경되면 `scraper.py` 수정 필요
- 과도한 크롤링은 IP 차단 위험이 있으므로 적절한 간격 유지
- `.env` 파일은 절대 공개 저장소에 업로드하지 말 것
- 환율 API가 응답하지 않을 경우 기본값 1,400원 사용

## 향후 개선 사항

- [ ] 스케줄러 추가 (주기적 자동 실행)
- [ ] AWS Lambda 배포 지원
- [ ] 여러 금 시세 사이트 지원
- [ ] 가격 알림 임계값 설정
- [ ] 데이터베이스 연동 (가격 이력 저장)
