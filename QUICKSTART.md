# 🚀 빠른 시작 가이드

바이낸스 테스트넷 봇을 5분 안에 실행해보세요!

## 📋 체크리스트

- [ ] Python 3.8 이상 설치
- [ ] 필요한 라이브러리 설치
- [ ] 테스트넷 API 키 발급
- [ ] 환경 변수 설정
- [ ] 테스트 자금 받기
- [ ] 봇 실행

---

## 1단계: 라이브러리 설치 (1분)

```bash
pip install -r requirements.txt
```

**확인 방법:**
```bash
python -c "import binance; print('✅ 설치 완료')"
```

---

## 2단계: 테스트넷 API 키 발급 (2분)

### 바이낸스 테스트넷 접속
🔗 https://testnet.binance.vision/

### 로그인
- GitHub 계정으로 로그인
- 별도 회원가입 불필요

### API 키 생성
1. "API Key" 메뉴 클릭
2. "Generate HMAC_SHA256 Key" 버튼 클릭
3. 키 이름 입력 (예: "MyTradingBot")
4. API Key와 Secret Key 복사 (⚠️ Secret Key는 다시 볼 수 없음!)

---

## 3단계: 환경 변수 설정 (1분)

### .env 파일 생성

```bash
# Windows
copy env_example.txt .env

# Mac/Linux
cp env_example.txt .env
```

### .env 파일 편집

메모장이나 에디터로 `.env` 파일을 열고 발급받은 API 키 입력:

```
BINANCE_TESTNET_API_KEY=여기에_발급받은_API_Key_입력
BINANCE_TESTNET_SECRET_KEY=여기에_발급받은_Secret_Key_입력
```

**⚠️ 주의**: 
- 따옴표 없이 직접 입력
- 공백 없이 입력

---

## 4단계: 테스트 자금 받기 (1분)

### 테스트넷에서 무료 자금 받기

1. https://testnet.binance.vision/ 접속
2. 우측 상단 "Get Test Funds" 버튼 클릭
3. 원하는 코인 선택:
   - BTC (Bitcoin)
   - ETH (Ethereum)
   - USDT (Tether)
   - BNB (Binance Coin)
4. "Get" 버튼 클릭

💡 **팁**: 모든 코인을 받아두세요! 무료이고 무제한입니다.

---

## 5단계: 연결 테스트 (30초)

봇 실행 전에 연결을 테스트해보세요:

```bash
python test_testnet_connection.py
```

**성공 시 출력:**
```
✅ API Key: abcd1234...
✅ Secret Key: xyz9876...
✅ 서버 연결 성공!
✅ 계정 타입: SPOT
✅ 거래 가능 여부: True
✅ 보유 자산:
  • BTC     :    10.00000000 (사용가능)
  • USDT    : 10000.00000000 (사용가능)
✅ BTC/USDT 현재가: $67,234.50
✅ 모든 테스트 통과!
```

**실패 시:**
- API 키 다시 확인
- .env 파일 내용 확인
- 인터넷 연결 확인

---

## 6단계: 봇 실행! 🚀

```bash
python binance_testnet_bot.py
```

**실행 화면:**
```
🔍 바이낸스 테스트넷 연결 테스트...
✅ 테스트넷 연결 성공!
📊 계정 상태: SPOT
==================================================
✅ 바이낸스 테스트넷 봇 초기화 완료
📊 거래 페어: BTCUSDT
💰 거래 수량: 0.001 BTC
🚀 바이낸스 테스트넷 봇 시작!
⏰ 체크 주기: 60초
📈 현재가: $67,234.50 | RSI: 45.23 | MACD: -12.34
```

---

## 🎮 봇 제어

### 봇 종료
```
Ctrl + C
```

봇이 안전하게 종료되고 거래 리포트가 자동 저장됩니다.

### 로그 확인
```bash
# Windows
type logs\testnet_trading_bot.log

# Mac/Linux
cat logs/testnet_trading_bot.log
```

### 거래 리포트 확인
`logs/trade_report_*.json` 파일에서 모든 거래 내역 확인

---

## 🔍 문제 해결

### "API 키가 설정되지 않았습니다"
→ `.env` 파일을 생성하고 API 키를 입력하세요

### "연결 실패: Invalid API-key"
→ API 키가 올바른지 확인하세요 (테스트넷 키여야 함)

### "주문 실패: Insufficient balance"
→ 테스트넷에서 무료 자금을 받으세요

### "FileNotFoundError: logs/"
→ logs 폴더 생성: `mkdir logs`

---

## 📚 더 알아보기

- **상세 가이드**: `README.md`
- **전략 설명**: RSI, MACD, 볼린저밴드 설명
- **고급 설정**: 다양한 커스터마이징 옵션

---

## ⚠️ 중요 알림

### ✅ 테스트넷은 완전히 안전합니다
- 실제 돈이 아님
- 손실 위험 없음
- 무제한 테스트 가능

### 🚨 실제 거래 전 주의
- 최소 1주일 테스트
- 승률과 손익비 분석
- 소액으로 시작
- 전액 투자 금지

---

## 🎉 이제 준비 완료!

질문이나 문제가 있으면 언제든지 물어보세요!

**Happy Trading! 🚀📈**


