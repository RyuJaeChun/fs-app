"""
회사 코드 다운로드 및 검색 예시
"""
from dart_api import DartAPI
import json

def download_corp_codes_example():
    """회사 코드 다운로드 예시"""
    print("=== 회사 코드 다운로드 예시 ===")
    
    dart = DartAPI()
    
    # 회사 코드 다운로드 (JSON 파일로 저장)
    corp_codes = dart.download_corp_codes(save_json=True)
    
    print(f"다운로드된 회사 수: {len(corp_codes)}")
    
    # 몇 개 회사 정보 출력
    print("\n처음 5개 회사 정보:")
    for i, (corp_code, corp_info) in enumerate(corp_codes.items()):
        if i >= 5:
            break
        print(f"  {corp_info['corp_name']} ({corp_info['corp_code']}) - 종목코드: {corp_info['stock_code']}")

def load_and_search_example():
    """저장된 회사 코드 로드 및 검색 예시"""
    print("\n=== 회사 검색 예시 ===")
    
    dart = DartAPI()
    
    # 저장된 JSON 파일에서 회사 코드 로드
    corp_codes = dart.load_corp_codes()
    
    if not corp_codes:
        print("회사 코드 파일이 없습니다. 먼저 download_corp_codes_example()을 실행해주세요.")
        return
    
    # 회사명으로 검색
    search_terms = ["삼성", "LG", "SK", "현대", "한국전력"]
    
    for term in search_terms:
        print(f"\n'{term}' 검색 결과:")
        results = dart.search_company(term, corp_codes)
        
        if results:
            print(f"  총 {len(results)}개 회사 발견")
            for i, company in enumerate(results[:5]):  # 상위 5개만 출력
                print(f"    {i+1}. {company['corp_name']} ({company['corp_code']}) - 종목코드: {company['stock_code']}")
            if len(results) > 5:
                print(f"    ... 외 {len(results) - 5}개 회사")
        else:
            print("  검색 결과가 없습니다.")

def search_specific_company():
    """특정 회사 찾기 예시"""
    print("\n=== 특정 회사 찾기 예시 ===")
    
    dart = DartAPI()
    corp_codes = dart.load_corp_codes()
    
    if not corp_codes:
        print("회사 코드 파일이 없습니다.")
        return
    
    # 정확한 회사명으로 검색
    companies_to_find = ["삼성전자", "SK하이닉스", "NAVER", "카카오", "셀트리온"]
    
    for company_name in companies_to_find:
        results = dart.search_company(company_name, corp_codes)
        
        # 정확히 일치하는 회사 찾기
        exact_match = None
        for result in results:
            if result['corp_name'] == company_name:
                exact_match = result
                break
        
        if exact_match:
            print(f"✓ {company_name}")
            print(f"    고유번호: {exact_match['corp_code']}")
            print(f"    종목코드: {exact_match['stock_code']}")
            print(f"    수정일자: {exact_match['modify_date']}")
        else:
            print(f"✗ {company_name} - 정확한 일치 없음")
            if results:
                print(f"    유사한 회사: {results[0]['corp_name']}")

def export_to_excel():
    """회사 코드를 Excel로 내보내기"""
    print("\n=== Excel 파일로 내보내기 ===")
    
    dart = DartAPI()
    
    # JSON 파일 로드
    try:
        with open('corpCodes.json', 'r', encoding='utf-8') as f:
            corp_list = json.load(f)
        
        # DataFrame으로 변환하여 Excel 저장
        import pandas as pd
        df = pd.DataFrame(corp_list)
        
        # 종목코드가 있는 회사만 필터링 (상장회사)
        listed_companies = df[df['stock_code'] != ''].copy()
        
        filename = 'listed_companies.xlsx'
        listed_companies.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"상장회사 {len(listed_companies)}개를 {filename}에 저장했습니다.")
        
        # 시장별 통계
        print("\n시장별 통계:")
        print(f"  전체 등록회사: {len(corp_list)}개")
        print(f"  상장회사: {len(listed_companies)}개")
        print(f"  비상장회사: {len(corp_list) - len(listed_companies)}개")
        
    except FileNotFoundError:
        print("corpCodes.json 파일이 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

def interactive_search():
    """대화형 회사 검색"""
    print("\n=== 대화형 회사 검색 ===")
    print("회사명을 입력하면 관련 회사를 검색합니다. (종료: 'q')")
    
    dart = DartAPI()
    corp_codes = dart.load_corp_codes()
    
    if not corp_codes:
        print("회사 코드 파일이 없습니다.")
        return
    
    while True:
        search_term = input("\n검색할 회사명: ").strip()
        
        if search_term.lower() == 'q':
            print("검색을 종료합니다.")
            break
        
        if not search_term:
            continue
        
        results = dart.search_company(search_term, corp_codes)
        
        if results:
            print(f"\n'{search_term}' 검색 결과 ({len(results)}개):")
            print("-" * 80)
            print(f"{'번호':<4} {'회사명':<30} {'고유번호':<10} {'종목코드':<8}")
            print("-" * 80)
            
            for i, company in enumerate(results[:20], 1):  # 최대 20개
                stock_code = company['stock_code'] if company['stock_code'] else '-'
                print(f"{i:<4} {company['corp_name']:<30} {company['corp_code']:<10} {stock_code:<8}")
            
            if len(results) > 20:
                print(f"... 외 {len(results) - 20}개 회사")
        else:
            print(f"'{search_term}'에 대한 검색 결과가 없습니다.")

if __name__ == "__main__":
    try:
        print("DART 회사 코드 다운로드 및 검색 예시")
        print("=" * 50)
        
        # 1. 회사 코드 다운로드
        download_corp_codes_example()
        
        # 2. 회사 검색
        load_and_search_example()
        
        # 3. 특정 회사 찾기
        search_specific_company()
        
        # 4. Excel로 내보내기
        export_to_excel()
        
        # 5. 대화형 검색 (옵션)
        choice = input("\n대화형 검색을 실행하시겠습니까? (y/n): ").strip().lower()
        if choice == 'y':
            interactive_search()
        
        print("\n모든 예시가 완료되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("API 키가 올바르게 설정되었는지 확인해주세요.")

