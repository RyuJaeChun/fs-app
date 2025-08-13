"""
웹 서버 실행 스크립트
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 재무제표 시각화 웹 애플리케이션을 시작합니다...")
    print("📍 접속 주소: http://localhost:8000")
    print("🔄 자동 새로고침이 활성화되었습니다.")
    print("⏹️  종료하려면 Ctrl+C를 누르세요.")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"],
        log_level="info"
    )

