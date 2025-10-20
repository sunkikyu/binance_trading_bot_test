"""
바이낸스 테스트넷 자동매매 봇
- RSI, MACD, 볼린저밴드 기반 기술적 분석
- 테스트넷 전용으로 안전한 테스트 가능
- 자동 손절/익절 시스템
- 실시간 로깅 및 트레이딩 리포트
"""

import os
import time
import json
import logging
from datetime import datetime
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
import os
import sys
import logging

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 로그 디렉토리 생성
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 로그 파일 경로
log_file = os.path.join(log_dir, 'testnet_trading_bot.log')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 로거 설정
logger = logging.getLogger(__name__)

# 초기 로그 메시지
logger.info("="*50)
logger.info("바이낸스 테스트넷 봇 로깅 시작")
logger.info("="*50)

class BinanceTestnetBot:
    def __init__(self):
        """바이낸스 테스트넷 봇 초기화"""
        # API 키 설정
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY')
        self.api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
        
        if not self.api_key or not self.api_secret:
            logger.error("❌ API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
            raise ValueError("API 키 누락")
        
        # 바이낸스 테스트넷 클라이언트 초기화
        self.client = Client(
            self.api_key, 
            self.api_secret,
            testnet=True  # 테스트넷 모드
        )
        
        # 테스트넷 URL 설정
        self.client.API_URL = 'https://testnet.binance.vision/api'
        
        # 거래 파라미터
        self.symbol = 'BTCUSDT'  # 거래 페어
        
        # 자산 및 거래 설정
        self.total_asset = 3_600  # 총 자산 (USD)
        self.daily_target = 20    # 일일 목표 수익 (USD)
        
        # 일일 수익 추적
        self.daily_profit = 0  # 오늘 누적 수익
        self.last_trade_date = None  # 마지막 거래 날짜
        
        # 현재 BTC 가격 조회 (실시간으로 가져오기)
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            btc_price = float(ticker['price'])
            
            # 거래 금액 계산 (총 자산의 2%)
            trade_amount = self.total_asset * 0.02
            self.quantity = round(trade_amount / btc_price, 5)
            
            logger.info(f"💰 총 자산: ${self.total_asset:,.2f}")
            logger.info(f"🎯 일일 목표 수익: ${self.daily_target:,.2f}")
            logger.info(f"💸 1회 거래 금액: ${trade_amount:,.2f}")
            logger.info(f"🔢 거래 수량: {self.quantity} BTC")
            logger.info(f"💵 현재 BTC 가격: ${btc_price:,.2f}")
        
        except Exception as e:
            # 기본값으로 설정
            self.quantity = 0.0001  # 소액으로 안전하게 설정
            logger.warning(f"❗ BTC 가격 조회 실패. 기본 거래 수량 사용: {self.quantity}")
        
        self.rsi_period = 14
        self.rsi_oversold = 30  # RSI 과매도 기준
        self.rsi_overbought = 70  # RSI 과매수 기준
        
        # 손익 설정
        self.take_profit_percent = 3.0  # 익절 3%
        self.stop_loss_percent = 1.5  # 손절 1.5%
        
        # 포지션 관리
        self.position = None
        self.trade_history = []
        
        logger.info("✅ 바이낸스 테스트넷 봇 초기화 완료")
        logger.info(f"📊 거래 페어: {self.symbol}")
        logger.info(f"💰 거래 수량: {self.quantity} BTC")
    
    def calculate_rsi(self, prices, period=14):
        """RSI(Relative Strength Index) 계산"""
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_macd(self, prices):
        """MACD(Moving Average Convergence Divergence) 계산"""
        prices_series = pd.Series(prices)
        
        ema_12 = prices_series.ewm(span=12, adjust=False).mean()
        ema_26 = prices_series.ewm(span=26, adjust=False).mean()
        
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        return macd_line.iloc[-1], signal_line.iloc[-1]
    
    def calculate_bollinger_bands(self, prices, period=20):
        """볼린저 밴드 계산"""
        prices_series = pd.Series(prices)
        
        sma = prices_series.rolling(window=period).mean()
        std = prices_series.rolling(window=period).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        return upper_band.iloc[-1], sma.iloc[-1], lower_band.iloc[-1]
    
    def get_market_data(self, interval='15m', limit=100):
        """시장 데이터 가져오기"""
        try:
            klines = self.client.get_klines(
                symbol=self.symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return df
        except Exception as e:
            logger.error(f"❌ 시장 데이터 가져오기 실패: {e}")
            return None
    
    def get_current_price(self):
        """현재 가격 조회"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"❌ 현재 가격 조회 실패: {e}")
            return None
    
    def analyze_market(self):
        """종합 시장 분석"""
        df = self.get_market_data()
        if df is None or len(df) < 50:
            return None
        
        prices = df['close'].values
        current_price = prices[-1]
        
        # 기술적 지표 계산
        rsi = self.calculate_rsi(prices, self.rsi_period)
        macd, signal = self.calculate_macd(prices)
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(prices)
        
        analysis = {
            'current_price': current_price,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': signal,
            'bb_upper': upper_bb,
            'bb_middle': middle_bb,
            'bb_lower': lower_bb,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"📈 현재가: ${current_price:,.2f} | RSI: {rsi:.2f} | MACD: {macd:.2f}")
        
        return analysis
    
    def is_daily_target_reached(self):
        """일일 목표 수익 달성 여부 확인"""
        # 날짜 확인 및 초기화
        today = datetime.now().date()
        
        # 날짜가 바뀌면 일일 수익 초기화
        if self.last_trade_date != today:
            self.daily_profit = 0
            self.last_trade_date = today
        
        # 일일 목표 수익 도달 여부 확인
        return self.daily_profit >= self.daily_target

    def generate_signal(self, analysis):
        """매수 신호 생성"""
        # 일일 목표 수익 달성 시 매수 금지
        if self.is_daily_target_reached():
            logger.info("🚫 오늘의 목표 수익 달성. 더 이상 매수하지 않습니다.")
            return None
            
        if not analysis:
            return None
            
        rsi = analysis['rsi']
        macd = analysis['macd']
        signal = analysis['macd_signal']
        current_price = analysis['current_price']
        bb_lower = analysis['bb_lower']
        bb_middle = analysis['bb_middle']
        bb_upper = analysis['bb_upper']
        
        # 상세 로깅: 현재 시장 상태
        logger.info("📊 현재 시장 상태:")
        logger.info(f"   💰 현재 가격: ${current_price:,.2f}")
        logger.info(f"   📈 RSI: {rsi:.2f}")
        logger.info(f"   📊 MACD: {macd:.2f}")
        logger.info(f"   🔔 MACD 시그널: {signal:.2f}")
        logger.info(f"   🟢 볼린저 밴드 하단: ${bb_lower:,.2f}")
        logger.info(f"   ⚪ 볼린저 밴드 중간: ${bb_middle:,.2f}")
        logger.info(f"   🔴 볼린저 밴드 상단: ${bb_upper:,.2f}")
        
        # 매수 신호 조건 상세 로깅
        logger.info("\n🕵️ 매수 신호 조건 분석:")
        
        # RSI 조건 확인 (과매도 상태)
        rsi_condition = rsi < 30  # 과매도 기준 30 미만
        logger.info(f"   1. RSI 조건: {rsi_condition}")
        logger.info(f"      - 현재 RSI: {rsi:.2f}")
        logger.info(f"      - 과매도 기준: 30")
        
        # MACD 조건 확인
        macd_condition = macd > signal
        logger.info(f"   2. MACD 조건: {macd_condition}")
        logger.info(f"      - MACD: {macd:.2f}")
        logger.info(f"      - MACD 시그널: {signal:.2f}")
        
        # 볼린저 밴드 조건 확인
        bb_condition = current_price <= bb_lower * 1.02
        logger.info(f"   3. 볼린저 밴드 조건: {bb_condition}")
        logger.info(f"      - 현재 가격: ${current_price:,.2f}")
        logger.info(f"      - 볼린저 밴드 하단: ${bb_lower:,.2f}")
        logger.info(f"      - 볼린저 밴드 하단 * 1.02: ${bb_lower * 1.02:,.2f}")
        
        # 최종 매수 신호 결정
        if (rsi_condition and macd_condition and bb_condition):
            logger.info("\n🟢 매수 신호 발생! 모든 조건 충족 🎉")
            return 'BUY'
            
        logger.info("\n🔴 매수 신호 없음. 조건 미충족")
        return None
    
    def place_order(self, side):
        """주문 실행 (테스트넷)"""
        try:
            order = self.client.order_market(
                symbol=self.symbol,
                side=side,
                quantity=self.quantity
            )
            
            logger.info(f"✅ {side} 주문 체결 성공!")
            logger.info(f"주문 ID: {order['orderId']}")
            logger.info(f"체결가: ${float(order['fills'][0]['price']):,.2f}")
            
            return order
        except Exception as e:
            logger.error(f"❌ 주문 실패: {e}")
            return None
    
    def open_position(self, side, price):
        """포지션 오픈"""
        order = self.place_order(side)
        
        if order:
            self.position = {
                'side': side,
                'entry_price': price,
                'quantity': self.quantity,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'order_id': order['orderId']
            }
            logger.info(f"🔓 포지션 오픈: {side} @ ${price:,.2f}")
            return True
        
        return False
    
    def check_position_exit(self):
        """포지션 청산 조건 확인"""
        if not self.position:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        # 손익 계산
        pnl_percent = ((current_price - self.position['entry_price']) / 
                       self.position['entry_price'] * 100)
        pnl_amount = (current_price - self.position['entry_price']) * self.quantity
        
        # 익절 조건: 3% 이상 수익 또는 20달러 이상 수익
        if (pnl_percent >= self.take_profit_percent or 
            pnl_amount >= self.daily_target):
            self.close_position(reason='익절')
        
        # 손절 조건: 1.5% 이상 손실
        elif pnl_percent <= -self.stop_loss_percent:
            self.close_position(reason='손절')
    
    def close_position(self, reason='manual'):
        """포지션 청산"""
        if not self.position:
            return False
        
        current_price = self.get_current_price()
        
        # 매도 주문
        order = self.place_order('SELL')
        
        if order:
            # 손익 계산
            pnl_percent = ((current_price - self.position['entry_price']) / 
                           self.position['entry_price'] * 100)
            pnl_amount = (current_price - self.position['entry_price']) * self.quantity
            
            # 일일 누적 수익 업데이트
            self.daily_profit += pnl_amount
            
            # 거래 기록 저장
            trade_record = {
                'open_time': self.position['time'],
                'close_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'side': 'BUY',  # 현물 매수 후 매도
                'entry_price': self.position['entry_price'],
                'exit_price': current_price,
                'quantity': self.quantity,
                'pnl_percent': pnl_percent,
                'pnl_amount': pnl_amount,
                'reason': reason,
                'daily_profit': self.daily_profit
            }
            
            self.trade_history.append(trade_record)
            
            logger.info(f"🔒 포지션 청산: {reason}")
            logger.info(f"💰 손익: {pnl_percent:+.2f}% (${pnl_amount:+.2f})")
            logger.info(f"📊 오늘의 누적 수익: ${self.daily_profit:,.2f}")
            
            self.position = None
            return True
        
        return False
    
    def save_trade_report(self):
        """거래 리포트 저장"""
        if not self.trade_history:
            return
        
        report_file = f'logs/trade_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.trade_history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 거래 리포트 저장: {report_file}")
    
    def run(self, check_interval=60):
        """봇 실행"""
        logger.info("🚀 바이낸스 현물 거래 봇 시작!")
        logger.info(f"⏰ 체크 주기: {check_interval}초")
        logger.info(f"💰 거래 수량: {self.quantity} BTC")
        logger.info(f"📊 거래 페어: {self.symbol}")
        
        try:
            while True:
                # 날짜 초기화 확인
                self.is_daily_target_reached()
                
                # 시장 분석
                analysis = self.analyze_market()
                
                if analysis:
                    # 기존 포지션이 있으면 청산 조건 확인
                    if self.position:
                        self.check_position_exit()
                    
                    # 포지션이 없으면 매수 신호 확인
                    else:
                        signal = self.generate_signal(analysis)
                        
                        if signal == 'BUY':
                            logger.info(f"🎯 매수 신호 발생!")
                            self.open_position(signal, analysis['current_price'])
                
                # 대기
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n⏹️ 봇 종료 요청")
            
            # 열린 포지션 청산
            if self.position:
                logger.info("📤 열린 포지션 청산 중...")
                self.close_position(reason='수동종료')
            
            # 거래 리포트 저장
            self.save_trade_report()
            
            logger.info("✅ 봇 종료 완료")
        
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            
            # 긴급 포지션 청산
            if self.position:
                self.close_position(reason='에러')
            
            self.save_trade_report()

def test_connection():
    """테스트넷 연결 테스트"""
    print("🔍 바이낸스 테스트넷 연결 테스트...")
    
    load_dotenv()
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
    
    if not api_key or not api_secret:
        print("❌ .env 파일에 API 키가 설정되지 않았습니다.")
        return False
    
    try:
        client = Client(api_key, api_secret, testnet=True)
        client.API_URL = 'https://testnet.binance.vision/api'
        
        # 계정 정보 조회
        account = client.get_account()
        print("✅ 테스트넷 연결 성공!")
        print(f"📊 계정 상태: {account['accountType']}")
        
        # 잔고 확인
        balances = [b for b in account['balances'] if float(b['free']) > 0]
        if balances:
            print("\n💰 보유 자산:")
            for balance in balances[:5]:
                print(f"  - {balance['asset']}: {float(balance['free']):.8f}")
        
        return True
    
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

if __name__ == "__main__":
    # 연결 테스트 먼저 수행
    if test_connection():
        print("\n" + "="*50)
        bot = BinanceTestnetBot()
        bot.run(check_interval=60)  # 60초마다 체크
    else:
        print("\n❌ 봇을 시작할 수 없습니다. API 설정을 확인하세요.")

