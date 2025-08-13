"""
DART API 사용 예시 스크립트
"""
from dart_api import DartAPI, get_recent_date_range, print_disclosure_summary

def example_basic_search():
    """기본 검색 예시"""
    print("=== 기본 검색 예시 ===")
    
    dart = DartAPI()
    
    # 최근 3일간의 공시 검색
    bgn_de, end_de = get_recent_date_range(3)
    
    result = dart.search_disclosure(
        bgn_de=bgn_de,
        end_de=end_de,
        corp_cls='Y',  # 유가증권시장
        page_count=20
    )
    
    if result['status'] == '000':
        print(f"검색 결과: {result['total_count']}건")
        if 'list' in result:
            print_disclosure_summary(result['list'])
    else:
        print(f"검색 실패: {result['message']}")

def example_company_search():
    """특정 회사 검색 예시"""
    print("\n=== 특정 회사 검색 예시 ===")
    
    dart = DartAPI()
    
    # 회사 코드 로드 (없으면 다운로드)
    try:
        corp_codes = dart.load_corp_codes()
    except:
        print("회사 코드를 다운로드합니다...")
        corp_codes = dart.download_corp_codes()
    
    # 삼성전자 찾기
    samsung_results = dart.search_company("삼성전자", corp_codes)
    if samsung_results:
        samsung = samsung_results[0]  # 첫 번째 결과 사용
        corp_code = samsung['corp_code']
        print(f"검색된 회사: {samsung['corp_name']} (고유번호: {corp_code})")
        
        # 최근 30일간의 공시
        bgn_de, end_de = get_recent_date_range(30)
        
        disclosures = dart.get_all_disclosures(
            corp_code=corp_code,
            bgn_de=bgn_de,
            end_de=end_de
        )
        
        print_disclosure_summary(disclosures)
        
        # CSV와 JSON으로 저장
        if disclosures:
            filename = f"samsung_disclosures_{bgn_de}_{end_de}"
            dart.save_data(disclosures, filename, 'csv')
            dart.save_data(disclosures, filename, 'json')
    else:
        print("삼성전자를 찾을 수 없습니다.")

def example_disclosure_type_search():
    """공시 유형별 검색 예시"""
    print("\n=== 공시 유형별 검색 예시 ===")
    
    dart = DartAPI()
    
    # 최근 7일간의 정기공시(A)만 검색
    bgn_de, end_de = get_recent_date_range(7)
    
    disclosures = dart.get_all_disclosures(
        bgn_de=bgn_de,
        end_de=end_de,
        pblntf_ty='A',  # 정기공시
        corp_cls='Y'    # 유가증권시장
    )
    
    print_disclosure_summary(disclosures)

def example_market_search():
    """시장별 검색 예시"""
    print("\n=== 시장별 검색 예시 ===")
    
    dart = DartAPI()
    bgn_de, end_de = get_recent_date_range(1)  # 어제 하루
    
    markets = {
        'Y': '유가증권시장',
        'K': '코스닥시장',
        'N': '코넥스시장'
    }
    
    for market_code, market_name in markets.items():
        print(f"\n{market_name} 공시:")
        
        result = dart.search_disclosure(
            bgn_de=bgn_de,
            end_de=end_de,
            corp_cls=market_code,
            page_count=5
        )
        
        if result['status'] == '000' and 'list' in result:
            print(f"총 {result['total_count']}건")
            for disclosure in result['list'][:3]:  # 상위 3건만 출력
                print(f"  - {disclosure['corp_name']}: {disclosure['report_nm']}")
        else:
            print("  조회된 공시가 없습니다.")

def example_save_to_files():
    """파일 저장 예시"""
    print("\n=== 파일 저장 예시 ===")
    
    dart = DartAPI()
    
    # 최근 5일간의 주요사항보고(B) 검색
    bgn_de, end_de = get_recent_date_range(5)
    
    disclosures = dart.get_all_disclosures(
        bgn_de=bgn_de,
        end_de=end_de,
        pblntf_ty='B',  # 주요사항보고
        corp_cls='Y'    # 유가증권시장
    )
    
    if disclosures:
        # 모든 형식으로 저장
        base_filename = f"major_disclosures_{bgn_de}_{end_de}"
        dart.save_data(disclosures, base_filename, 'all')  # CSV, Excel, JSON 모두 저장
        
        # DataFrame으로 변환해서 간단한 분석
        df = dart.to_dataframe(disclosures)
        print(f"\n분석 결과:")
        print(f"- 총 공시 건수: {len(df)}")
        print(f"- 참여 회사 수: {df['corp_name'].nunique()}")
        print(f"- 가장 많이 공시한 회사: {df['corp_name'].value_counts().head(1).index[0] if not df.empty else 'N/A'}")

if __name__ == "__main__":
    try:
        print("DART Open API 사용 예시를 실행합니다.\n")
        print("API 키가 설정되어 있는지 확인해주세요.")
        print("(.env 파일에 DART_API_KEY 설정 또는 환경변수 설정)\n")
        
        # 모든 예시 실행
        example_basic_search()
        example_company_search()
        example_disclosure_type_search()
        example_market_search()
        example_save_to_files()
        
        print("\n모든 예시가 완료되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. DART Open API 키가 올바르게 설정되었는지 확인")
        print("2. 인터넷 연결 상태 확인")
        print("3. API 키 유효성 및 사용 한도 확인")
