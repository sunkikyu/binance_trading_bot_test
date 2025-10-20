# -*- coding: utf-8 -*-
"""
바이낸스 테스트넷 연결 테스트 스크립트
봇 실행 전에 API 키와 연결 상태를 확인하세요.
"""

import os
import sys
from binance.client import Client
from dotenv import load_dotenv

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_testnet_connection():
    """테스트넷 연결 및 계정 정보 확인"""
    print("="*60)
    print("바이낸스 테스트넷 연결 테스트")
    print("="*60)
    
    # 환경 변수 로드
    load_dotenv()
    
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
    
    # API 키 확인
    print("\n1. API 키 확인...")
    if not api_key or not api_secret:
        print("실패: .env 파일에 API 키가 설정되지 않았습니다.")
        print("\n해결 방법:")
        print("  1. .env 파일을 생성하세요 (env_example.txt 참고)")
        print("  2. https://testnet.binance.vision/ 에서 API 키 발급")
        print("  3. .env 파일에 API 키를 입력하세요")
        return False
    
    print(f"성공: API Key: {api_key[:8]}...")
    print(f"성공: Secret Key: {api_secret[:8]}...")
    
    # 테스트넷 연결
    print("\n2. 테스트넷 연결 시도...")
    try:
        client = Client(api_key, api_secret, testnet=True)
        client.API_URL = 'https://testnet.binance.vision/api'
        
        # 서버 시간 확인
        server_time = client.get_server_time()
        print(f"성공: 서버 연결 성공! (Server Time: {server_time['serverTime']})")
        
    except Exception as e:
        print(f"실패: 연결 실패: {e}")
        print("\n가능한 원인:")
        print("  - API 키가 올바르지 않음")
        print("  - 테스트넷 API 키가 아님 (실제 거래소 키와 다름)")
        print("  - 인터넷 연결 문제")
        return False
    
    # 계정 정보 조회
    print("\n3. 계정 정보 조회...")
    try:
        account = client.get_account()
        print(f"성공: 계정 타입: {account['accountType']}")
        print(f"성공: 거래 가능 여부: {account['canTrade']}")
        
    except Exception as e:
        print(f"실패: 계정 정보 조회 실패: {e}")
        return False
    
    # 잔고 확인
    print("\n4. 잔고 확인...")
    balances = [b for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
    
    if balances:
        print("보유 자산:")
        total_assets = 0
        for balance in balances:
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            if total > 0:
                print(f"  - {balance['asset']:8s}: {free:15.8f} (사용가능) + {locked:15.8f} (거래중) = {total:15.8f}")
                total_assets += 1
        
        print(f"\n총 {total_assets}개 자산 보유")
    else:
        print("경고: 잔고가 없습니다.")
        print("\n테스트 자금 받는 방법:")
        print("  1. https://testnet.binance.vision/ 접속")
        print("  2. GitHub 계정으로 로그인")
        print("  3. 우측 상단 'Get Test Funds' 클릭")
        print("  4. BTC, ETH, USDT 등 무료로 받기")
    
    # 시장 데이터 테스트
    print("\n5. 시장 데이터 테스트...")
    try:
        ticker = client.get_symbol_ticker(symbol='BTCUSDT')
        print(f"성공: BTC/USDT 현재가: ${float(ticker['price']):,.2f}")
        
        # 최근 거래 내역
        trades = client.get_recent_trades(symbol='BTCUSDT', limit=1)
        print(f"성공: 최근 거래: {len(trades)}건 조회 성공")
        
    except Exception as e:
        print(f"실패: 시장 데이터 조회 실패: {e}")
        return False
    
    # 최종 결과
    print("\n" + "="*60)
    print("모든 테스트 통과!")
    print("="*60)
    print("\n이제 봇을 실행할 준비가 되었습니다:")
    print("   python binance_testnet_bot.py")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        test_testnet_connection()
    except KeyboardInterrupt:
        print("\n\n테스트 중단")
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()

