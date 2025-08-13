"""
서버 테스트 스크립트
"""
import requests
import time

def test_server():
    """서버 상태 테스트"""
    print("🔍 서버 상태를 확인합니다...")
    
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다!")
            print(f"📍 접속 주소: http://localhost:8000")
            print(f"📊 응답 시간: {response.elapsed.total_seconds():.2f}초")
            print("🌟 웹 브라우저에서 위 주소로 접속하세요!")
        else:
            print(f"⚠️  서버 응답 오류: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("🔄 서버가 아직 시작 중일 수 있습니다. 잠시 후 다시 시도해주세요.")
    except requests.exceptions.Timeout:
        print("⏰ 서버 응답 시간 초과")
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_server()

