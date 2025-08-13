#!/usr/bin/env python3
"""
로컬 테스트용 간단한 서버 실행 스크립트
"""
import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 로컬 테스트 서버를 시작합니다...")
    print("📍 접속 주소: http://127.0.0.1:8003")
    print("⏹️  종료하려면 Ctrl+C를 누르세요.")
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8003,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✅ 서버가 정상적으로 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류: {e}")
