"""
서버 문제 진단 및 빠른 테스트
"""
import sys
import os

def test_imports():
    """모듈 import 테스트"""
    print("📦 모듈 import 테스트...")
    
    try:
        print("  - dart_api 테스트...", end="")
        from dart_api import DartAPI
        print(" ✅")
        
        print("  - database 테스트...", end="")
        from database import CompanyDatabase
        print(" ✅")
        
        print("  - financial_analyzer 테스트...", end="")
        from financial_analyzer import FinancialAnalyzer
        print(" ✅")
        
        return True
    except Exception as e:
        print(f" ❌ {e}")
        return False

def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n🔧 기본 기능 테스트...")
    
    try:
        from dart_api import DartAPI
        from database import CompanyDatabase
        
        print("  - DART API 초기화...", end="")
        dart = DartAPI()
        print(" ✅")
        
        print("  - 데이터베이스 초기화...", end="")
        db = CompanyDatabase()
        print(" ✅")
        
        print("  - 회사 검색 테스트...", end="")
        companies = db.search_companies("삼성", limit=1)
        if companies:
            print(" ✅")
            return True
        else:
            print(" ⚠️ (데이터 없음)")
            return False
            
    except Exception as e:
        print(f" ❌ {e}")
        return False

def test_ai_analyzer():
    """AI 분석기 테스트"""
    print("\n🤖 AI 분석기 테스트...")
    
    try:
        print("  - Gemini API 키 확인...", end="")
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            print(" ✅")
        else:
            print(" ❌ (API 키 미설정)")
            return False
        
        print("  - FinancialAnalyzer 초기화...", end="")
        from financial_analyzer import FinancialAnalyzer
        analyzer = FinancialAnalyzer()
        print(" ✅")
        
        return True
        
    except Exception as e:
        print(f" ❌ {e}")
        return False

def run_simple_server():
    """간단한 서버 실행"""
    print("\n🚀 간단한 서버 실행...")
    
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        import uvicorn
        
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"status": "ok", "message": "서버가 정상 작동 중입니다!"}
        
        @app.get("/test")
        async def test():
            return {"test": "success", "modules": "all loaded"}
        
        print("📍 http://localhost:8001에서 테스트 서버 실행")
        print("🔍 브라우저에서 http://localhost:8001/test 접속해보세요")
        print("⏹️ 종료하려면 Ctrl+C를 누르세요")
        
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")

def main():
    """메인 진단 프로세스"""
    print("🔍 서버 문제 진단 시작")
    print("=" * 50)
    
    # 1. Import 테스트
    if not test_imports():
        print("\n❌ 모듈 import 실패. 패키지 설치를 확인해주세요.")
        return
    
    # 2. 기본 기능 테스트
    if not test_basic_functionality():
        print("\n❌ 기본 기능 테스트 실패.")
        return
    
    # 3. AI 분석기 테스트 (선택사항)
    ai_ok = test_ai_analyzer()
    if not ai_ok:
        print("\n⚠️ AI 분석기는 비활성화됩니다. 기본 기능은 사용 가능합니다.")
    
    print("\n✅ 진단 완료!")
    
    # 4. 테스트 서버 실행 여부 묻기
    choice = input("\n간단한 테스트 서버를 실행하시겠습니까? (y/n): ").lower()
    if choice == 'y':
        run_simple_server()
    else:
        print("👋 진단을 종료합니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 진단을 중단합니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")

