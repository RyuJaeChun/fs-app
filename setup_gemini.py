"""
Gemini API 키 설정 도우미
"""
import os

def setup_gemini_api():
    """Gemini API 키 설정"""
    print("🤖 Gemini AI 설정 도우미")
    print("=" * 50)
    
    # .env 파일 확인
    env_file = ".env"
    env_content = ""
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        print(f"✓ {env_file} 파일이 존재합니다.")
    else:
        print(f"⚠️ {env_file} 파일이 없습니다. 새로 생성합니다.")
    
    # GEMINI_API_KEY 확인
    if 'GEMINI_API_KEY' in env_content and not 'your_gemini_api_key_here' in env_content:
        print("✓ GEMINI_API_KEY가 이미 설정되어 있습니다.")
        return
    
    print("\n🔑 Gemini API 키 설정이 필요합니다.")
    print("📋 Gemini API 키 발급 방법:")
    print("1. https://makersuite.google.com/app/apikey 방문")
    print("2. Google 계정으로 로그인")
    print("3. 'Create API Key' 클릭")
    print("4. 생성된 API 키 복사")
    
    print("\n" + "="*50)
    api_key = input("Gemini API 키를 입력하세요: ").strip()
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ 올바른 API 키를 입력해주세요.")
        return False
    
    # .env 파일 업데이트
    new_content = ""
    
    if env_content:
        # 기존 내용에서 GEMINI_API_KEY 업데이트
        lines = env_content.split('\n')
        gemini_updated = False
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY'):
                new_content += f"GEMINI_API_KEY={api_key}\n"
                gemini_updated = True
            else:
                new_content += line + "\n"
        
        if not gemini_updated:
            new_content += f"\n# Gemini AI API 키\nGEMINI_API_KEY={api_key}\n"
    else:
        # 새 .env 파일 생성
        new_content = f"""# DART Open API 인증키
DART_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini AI API 키
GEMINI_API_KEY={api_key}
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(new_content.strip() + '\n')
        
        print("✅ Gemini API 키가 성공적으로 설정되었습니다!")
        print("🔄 서버를 재시작하면 AI 분석 기능을 사용할 수 있습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return False

def test_gemini_api():
    """Gemini API 연결 테스트"""
    print("\n🧪 Gemini API 연결 테스트...")
    
    try:
        from financial_analyzer import FinancialAnalyzer
        
        analyzer = FinancialAnalyzer()
        print("✅ Gemini API 연결 성공!")
        print("🤖 AI 재무분석 기능을 사용할 수 있습니다.")
        return True
        
    except ValueError as e:
        print(f"❌ API 키 오류: {e}")
        print("💡 해결방법: API 키를 다시 확인하고 설정해주세요.")
        return False
    except Exception as e:
        print(f"❌ 연결 테스트 실패: {e}")
        print("💡 해결방법:")
        print("   1. 인터넷 연결 확인")
        print("   2. API 키 유효성 확인")
        print("   3. Gemini API 서비스 상태 확인")
        return False

def show_usage_guide():
    """사용법 가이드"""
    print("\n📖 AI 재무분석 사용법:")
    print("=" * 50)
    print("1. 웹 브라우저에서 http://localhost:8000 접속")
    print("2. 원하는 회사 검색 및 선택")
    print("3. 회사 페이지에서 'AI 분석 시작' 버튼 클릭")
    print("4. AI가 생성한 쉬운 재무분석 결과 확인")
    
    print("\n🎯 AI 분석 내용:")
    print("- 📊 한줄 요약: 회사 상태를 쉽게 설명")
    print("- 💪 재무적 강점: 회사의 장점들")
    print("- ⚠️ 주의사항: 투자시 고려할 위험요소")
    print("- 💡 투자의견: 일반투자자를 위한 조언")

if __name__ == "__main__":
    try:
        setup_gemini_api()
        test_gemini_api()
        show_usage_guide()
        
    except KeyboardInterrupt:
        print("\n\n👋 설정을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

