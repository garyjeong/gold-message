# Gold Message - 금·은 시세 텔레그램 알림

국제 금·은 실시간 시세를 기반으로 금은방 매매가격을 계산하여 텔레그램으로 발송하는 봇

## 기능

- 국제 금·은 실시간 시세 조회 (goldprice.org)
- USD/KRW 환율 조회 + 전일대비 변동 표시 (frankfurter.app)
- 금은방 매매가격 계산 (살 때 / 팔 때)
- 금: 1돈(3.75g) 기준, 은: 1g 기준 원화 환산
- 금·은 차트 링크 제공 (kr.investing.com)
- 하루 4회 텔레그램 자동 알림 (08:00, 11:00, 14:00, 17:00 KST)
- Fly.io 배포

## 메시지 형식

```
🏆 금·은 시세

[ 금 · 1돈(3.75g) ]
🏪 살 때: 1,018,874원
💰 팔 때: 846,108원
🔺 전일대비: +10,563원 (+1.21%)

[ 은 · 1g ]
🏪 살 때: 4,410원
💰 팔 때: 3,662원
🔺 전일대비: +178원 (+4.86%)

💱 환율: 1,462.05 KRW/USD (-5.37원, -0.37%)
⏰ 조회: 2026-02-10 12:15:43

📈 금 차트 | 은 차트
```

## 설정 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

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
```

## 실행 방법

```bash
python3 src/main.py
```

## 프로젝트 구조

```
gold-message/
├── src/
│   ├── scraper.py       # 국제 금·은 시세 및 환율 조회
│   ├── telegram_bot.py  # 텔레그램 발송
│   ├── formatter.py     # 메시지 포맷팅
│   └── main.py          # 스케줄러 및 메인 실행
├── config/
│   ├── .env             # 환경 변수 (생성 필요)
│   └── .env.example     # 환경 변수 예제
├── Dockerfile
├── fly.toml             # Fly.io 배포 설정
├── requirements.txt
└── README.md
```

## 주요 모듈

### scraper.py
- goldprice.org에서 금(XAU)·은(XAG) 실시간 국제시세 조회
- frankfurter.app에서 USD/KRW 환율 + 전일 환율 조회
- 금: 트로이온스 → 1돈(3.75g) 원화 환산
- 은: 트로이온스 → 1g 원화 환산
- 금은방 마진율 적용 (살 때 +15%, 팔 때 -4.5%)

### formatter.py
- 금·은 금은방 매매가격, 전일대비, 환율 변동을 텔레그램 메시지로 포맷팅
- kr.investing.com 차트 링크 포함

### telegram_bot.py
- python-telegram-bot 라이브러리 사용
- 비동기 메시지 발송 지원

## 주의사항

- `.env` 파일은 절대 공개 저장소에 업로드하지 말 것
- 금은방 마진율(살 때 +15%, 팔 때 -4.5%)은 업소마다 다를 수 있으므로 참고용
- 환율 API 미응답 시 기본값 1,400원 사용
