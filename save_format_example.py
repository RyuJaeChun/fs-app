"""
다양한 저장 형식 예시 스크립트
CSV, JSON, Excel 형식으로 데이터를 저장하는 방법을 보여줍니다.
"""
from dart_api import DartAPI, get_recent_date_range, print_disclosure_summary

def demonstrate_save_formats():
    """다양한 저장 형식 시연"""
    print("=== 다양한 저장 형식 시연 ===")
    
    dart = DartAPI()
    
    # 최근 3일간의 코스닥 공시 검색 (데이터 양을 적당히 유지)
    bgn_de, end_de = get_recent_date_range(3)
    
    print(f"기간: {bgn_de} ~ {end_de}")
    print("코스닥시장 공시를 검색합니다...")
    
    disclosures = dart.get_all_disclosures(
        bgn_de=bgn_de,
        end_de=end_de,
        corp_cls='K',  # 코스닥시장
        page_count=50  # 적당한 양만 가져오기
    )
    
    if not disclosures:
        print("검색된 공시가 없습니다.")
        return
    
    print_disclosure_summary(disclosures)
    
    base_filename = f"kosdaq_disclosures_{bgn_de}_{end_de}"
    
    print(f"\n저장 예시:")
    print("=" * 50)
    
    # 1. CSV 형식으로 저장
    print("1. CSV 형식으로 저장...")
    dart.save_data(disclosures, base_filename, 'csv')
    
    # 2. JSON 형식으로 저장
    print("\n2. JSON 형식으로 저장...")
    dart.save_data(disclosures, base_filename, 'json')
    
    # 3. Excel 형식으로 저장
    print("\n3. Excel 형식으로 저장...")
    dart.save_data(disclosures, base_filename, 'excel')
    
    # 4. 모든 형식으로 한번에 저장
    print("\n4. 모든 형식으로 한번에 저장...")
    all_filename = f"all_formats_{bgn_de}_{end_de}"
    dart.save_data(disclosures, all_filename, 'all')
    
    # 저장된 파일들 안내
    print(f"\n📁 저장된 파일들:")
    print(f"  - {base_filename}.csv")
    print(f"  - {base_filename}.json")
    print(f"  - {base_filename}.xlsx")
    print(f"  - {all_filename}.csv")
    print(f"  - {all_filename}.json")
    print(f"  - {all_filename}.xlsx")

def compare_file_formats():
    """파일 형식별 특징 비교"""
    print("\n=== 파일 형식별 특징 ===")
    print("=" * 50)
    
    formats = {
        'CSV': {
            'extension': '.csv',
            'pros': ['Excel에서 바로 열기 가능', '파일 크기 작음', '다양한 도구에서 지원'],
            'cons': ['데이터 타입 정보 손실', '복잡한 구조 표현 어려움'],
            'best_for': '데이터 분석, Excel 작업'
        },
        'JSON': {
            'extension': '.json',
            'pros': ['데이터 구조 보존', '프로그래밍에서 사용 편리', '웹 API와 호환'],
            'cons': ['파일 크기 상대적으로 큼', 'Excel에서 직접 열기 어려움'],
            'best_for': '프로그래밍, API 연동'
        },
        'Excel': {
            'extension': '.xlsx',
            'pros': ['Excel에서 완벽 지원', '서식 적용 가능', '일반 사용자 친화적'],
            'cons': ['파일 크기 큼', '프로그래밍에서 처리 복잡'],
            'best_for': '보고서 작성, 일반 사용자'
        }
    }
    
    for format_name, info in formats.items():
        print(f"\n{format_name} ({info['extension']}):")
        print(f"  장점: {', '.join(info['pros'])}")
        print(f"  단점: {', '.join(info['cons'])}")
        print(f"  적합한 용도: {info['best_for']}")

def save_by_company_type():
    """회사 유형별로 데이터를 나누어 저장"""
    print("\n=== 회사 유형별 저장 예시 ===")
    
    dart = DartAPI()
    
    # 최근 1일간의 모든 시장 공시
    bgn_de, end_de = get_recent_date_range(1)
    
    markets = {
        'Y': '유가증권시장',
        'K': '코스닥시장',
        'N': '코넥스시장'
    }
    
    for market_code, market_name in markets.items():
        print(f"\n{market_name} 공시를 검색합니다...")
        
        disclosures = dart.get_all_disclosures(
            bgn_de=bgn_de,
            end_de=end_de,
            corp_cls=market_code
        )
        
        if disclosures:
            # 시장별로 파일명 생성
            filename = f"{market_name.replace('시장', '')}_{bgn_de}"
            
            # JSON 형식으로 저장 (API 데이터 특성상 JSON이 적합)
            dart.save_data(disclosures, filename, 'json')
            
            print(f"  → {len(disclosures)}건 저장됨")
        else:
            print(f"  → 공시 없음")

def custom_json_save():
    """사용자 정의 JSON 저장 예시"""
    print("\n=== 사용자 정의 JSON 저장 ===")
    
    dart = DartAPI()
    
    # 최근 2일간의 주요사항보고만 검색
    bgn_de, end_de = get_recent_date_range(2)
    
    disclosures = dart.get_all_disclosures(
        bgn_de=bgn_de,
        end_de=end_de,
        pblntf_ty='B'  # 주요사항보고
    )
    
    if disclosures:
        # 기본 JSON 저장
        dart.save_to_json(disclosures, f"major_reports_{bgn_de}_{end_de}.json")
        
        # 압축된 JSON 저장 (들여쓰기 없음)
        dart.save_to_json(disclosures, f"major_reports_compact_{bgn_de}_{end_de}.json", indent=0)
        
        # 예쁘게 들여쓰기된 JSON 저장
        dart.save_to_json(disclosures, f"major_reports_pretty_{bgn_de}_{end_de}.json", indent=4)
        
        print("다양한 JSON 형식으로 저장 완료:")
        print("  - 기본 (들여쓰기 2)")
        print("  - 압축 (들여쓰기 0)")
        print("  - 예쁘게 (들여쓰기 4)")

def interactive_format_choice():
    """대화형 저장 형식 선택"""
    print("\n=== 대화형 저장 형식 선택 ===")
    
    print("저장할 형식을 선택해주세요:")
    print("1. CSV")
    print("2. JSON")
    print("3. Excel")
    print("4. 모든 형식")
    print("5. 건너뛰기")
    
    while True:
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == '5':
            print("저장을 건너뜁니다.")
            return
        
        if choice in ['1', '2', '3', '4']:
            break
        
        print("올바른 번호를 선택해주세요.")
    
    # 간단한 데이터로 테스트
    dart = DartAPI()
    bgn_de, end_de = get_recent_date_range(1)
    
    disclosures = dart.get_all_disclosures(
        bgn_de=bgn_de,
        end_de=end_de,
        corp_cls='Y',
        page_count=10  # 적은 데이터로 테스트
    )
    
    if not disclosures:
        print("검색된 데이터가 없습니다.")
        return
    
    filename = f"user_choice_{bgn_de}_{end_de}"
    
    format_map = {
        '1': 'csv',
        '2': 'json', 
        '3': 'excel',
        '4': 'all'
    }
    
    selected_format = format_map[choice]
    dart.save_data(disclosures, filename, selected_format)
    
    print(f"선택한 형식({selected_format})으로 저장 완료!")

if __name__ == "__main__":
    try:
        print("DART API 저장 형식 예시")
        print("=" * 50)
        
        # 1. 기본 저장 형식 시연
        demonstrate_save_formats()
        
        # 2. 파일 형식 특징 비교
        compare_file_formats()
        
        # 3. 회사 유형별 저장
        save_by_company_type()
        
        # 4. 사용자 정의 JSON 저장
        custom_json_save()
        
        # 5. 대화형 선택 (옵션)
        choice = input("\n대화형 형식 선택을 실행하시겠습니까? (y/n): ").strip().lower()
        if choice == 'y':
            interactive_format_choice()
        
        print("\n✅ 모든 저장 형식 예시가 완료되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("API 키가 올바르게 설정되었는지 확인해주세요.")

