<<<<<<< HEAD
# Binance Testnet Trading Bot

## 프로젝트 소개
이 프로젝트는 바이낸스 테스트넷에서 작동하는 암호화폐 자동 거래 봇입니다. RSI, MACD, 볼린저 밴드 등 다양한 기술적 지표를 활용하여 매수 신호를 생성합니다.

## 주요 기능
- 바이낸스 테스트넷 연결
- RSI 기반 매수 신호 생성
- MACD 모멘텀 분석
- 볼린저 밴드를 활용한 가격 변동성 평가
- 일일 수익 목표 설정
- 상세한 로깅 및 모니터링

## 시작하기

### 필수 조건
- Python 3.8+
- Binance Testnet API 키

### 설치
1. 저장소 클론
```bash
git clone https://github.com/[사용자명]/Binance_Trading_Bot.git
cd Binance_Trading_Bot
```

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 종속성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 정보를 입력:
```
BINANCE_TESTNET_API_KEY=your_api_key
BINANCE_TESTNET_SECRET_KEY=your_secret_key
```

### 실행
```bash
python binance_testnet_bot.py
```

## 구성
- `binance_testnet_bot.py`: 메인 거래 봇 스크립트
- `requirements.txt`: 필요한 Python 패키지 목록
- `.env`: API 키 및 민감한 정보 저장

## 주의사항
- 이 봇은 테스트넷에서만 작동합니다
- 실제 거래에 사용하기 전 철저한 테스트 필요
- 암호화폐 거래에는 항상 위험이 따릅니다

## 라이선스
MIT 라이선스 참조

## 기여
풀 리퀘스트는 언제나 환영입니다!


=======
# binance_trading_bot_test
>>>>>>> 458fb4eef5488877a8f0af4dafb67689515f042b
