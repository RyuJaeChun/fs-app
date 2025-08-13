"""
DART API 설정 도우미 스크립트
"""
import os

def setup_environment():
    """환경 설정 도우미"""
    print("DART Open API 설정 도우미")
    print("=" * 50)
    
    # .env 파일 존재 확인
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✓ {env_file} 파일이 이미 존재합니다.")
        
        # 기존 API 키 확인
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'DART_API_KEY' in content:
                    print("✓ DART_API_KEY가 설정되어 있습니다.")
                    return
        except:
            pass
    
    # API 키 입력 받기
    print("\nDART Open API 키를 설정해야 합니다.")
    print("API 키는 https://opendart.fss.or.kr/ 에서 발급받으실 수 있습니다.")
    print("(회원가입 → 인증키 신청 → 승인 후 사용 가능)")
    
    api_key = input("\nDART API 키를 입력해주세요 (40자리): ").strip()
    
    if len(api_key) != 40:
        print("❌ API 키는 40자리여야 합니다.")
        return False
    
    # .env 파일 생성/업데이트
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"# DART Open API 인증키\n")
            f.write(f"DART_API_KEY={api_key}\n")
        
        print(f"✓ {env_file} 파일에 API 키가 저장되었습니다.")
        print("이제 dart_api.py를 사용하실 수 있습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return False

def test_api_connection():
    """API 연결 테스트"""
    print("\nAPI 연결을 테스트합니다...")
    
    try:
        from dart_api import DartAPI
        
        dart = DartAPI()
        
        # 간단한 검색으로 테스트
        result = dart.search_disclosure(
            corp_cls='Y',
            page_count=1
        )
        
        if result['status'] == '000':
            print("✓ API 연결 성공!")
            print(f"✓ 현재 조회 가능한 공시: {result.get('total_count', 0)}건")
            return True
        else:
            print(f"❌ API 오류: {result['status']} - {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 연결 테스트 실패: {e}")
        return False

def show_api_status_codes():
    """API 상태 코드 설명"""
    print("\nDART API 상태 코드:")
    print("-" * 50)
    
    status_codes = {
        '000': '정상',
        '010': '등록되지 않은 키입니다.',
        '011': '사용할 수 없는 키입니다.',
        '012': '접근할 수 없는 IP입니다.',
        '013': '조회된 데이타가 없습니다.',
        '020': '요청 제한을 초과하였습니다.',
        '021': '조회 가능한 회사 개수가 초과하였습니다.',
        '100': '필드의 부적절한 값입니다.',
        '800': '시스템 점검으로 인한 서비스가 중지 중입니다.',
        '900': '정의되지 않은 오류가 발생하였습니다.'
    }
    
    for code, message in status_codes.items():
        print(f"{code}: {message}")

def show_disclosure_types():
    """공시 유형 설명"""
    print("\n공시 유형 (pblntf_ty):")
    print("-" * 50)
    
    types = {
        'A': '정기공시',
        'B': '주요사항보고', 
        'C': '발행공시',
        'D': '지분공시',
        'E': '기타공시',
        'F': '외부감사관련',
        'G': '펀드공시',
        'H': '자산유동화',
        'I': '거래소공시',
        'J': '공정위공시'
    }
    
    for code, name in types.items():
        print(f"{code}: {name}")

def show_corp_classes():
    """법인 구분 설명"""
    print("\n법인 구분 (corp_cls):")
    print("-" * 50)
    
    classes = {
        'Y': '유가증권시장',
        'K': '코스닥시장', 
        'N': '코넥스시장',
        'E': '기타'
    }
    
    for code, name in classes.items():
        print(f"{code}: {name}")

def main():
    """메인 설정 프로세스"""
    print("DART Open API 프로젝트 설정")
    print("=" * 50)
    
    while True:
        print("\n메뉴를 선택해주세요:")
        print("1. 환경 설정 (.env 파일 생성)")
        print("2. API 연결 테스트")
        print("3. API 상태 코드 보기")
        print("4. 공시 유형 보기")
        print("5. 법인 구분 보기")
        print("0. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == '1':
            setup_environment()
        elif choice == '2':
            test_api_connection()
        elif choice == '3':
            show_api_status_codes()
        elif choice == '4':
            show_disclosure_types()
        elif choice == '5':
            show_corp_classes()
        elif choice == '0':
            print("설정을 종료합니다.")
            break
        else:
            print("올바른 번호를 선택해주세요.")

if __name__ == "__main__":
    main()

