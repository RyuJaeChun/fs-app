"""
DART Open API를 사용한 공시검색 및 데이터 다운로드 모듈
"""
import os
import requests
import json
import pandas as pd
import zipfile
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class DartAPI:
    """DART Open API 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        DART API 초기화
        
        Args:
            api_key: DART API 인증키. 없으면 환경변수에서 가져옴
        """
        self.api_key = api_key or os.getenv('DART_API_KEY')
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. 환경변수 DART_API_KEY를 설정하거나 직접 전달해주세요.")
        
        self.base_url = "https://opendart.fss.or.kr/api"
        
    def search_disclosure(self,
                         corp_code: Optional[str] = None,
                         bgn_de: Optional[str] = None,
                         end_de: Optional[str] = None,
                         last_reprt_at: str = "N",
                         pblntf_ty: Optional[str] = None,
                         pblntf_detail_ty: Optional[str] = None,
                         corp_cls: Optional[str] = None,
                         sort: str = "date",
                         sort_mth: str = "desc",
                         page_no: int = 1,
                         page_count: int = 10) -> Dict[str, Any]:
        """
        공시검색 API 호출
        
        Args:
            corp_code: 고유번호(8자리)
            bgn_de: 시작일(YYYYMMDD)
            end_de: 종료일(YYYYMMDD)
            last_reprt_at: 최종보고서 검색여부(Y/N)
            pblntf_ty: 공시유형(A~J)
            pblntf_detail_ty: 공시상세유형(4자리)
            corp_cls: 법인구분(Y/K/N/E)
            sort: 정렬(date/crp/rpt)
            sort_mth: 정렬방법(asc/desc)
            page_no: 페이지 번호
            page_count: 페이지별 건수(1~100)
            
        Returns:
            API 응답 결과
        """
        url = f"{self.base_url}/list.json"
        
        params = {
            'crtfc_key': self.api_key,
            'last_reprt_at': last_reprt_at,
            'sort': sort,
            'sort_mth': sort_mth,
            'page_no': page_no,
            'page_count': page_count
        }
        
        # 선택적 파라미터 추가
        if corp_code:
            params['corp_code'] = corp_code
        if bgn_de:
            params['bgn_de'] = bgn_de
        if end_de:
            params['end_de'] = end_de
        if pblntf_ty:
            params['pblntf_ty'] = pblntf_ty
        if pblntf_detail_ty:
            params['pblntf_detail_ty'] = pblntf_detail_ty
        if corp_cls:
            params['corp_cls'] = corp_cls
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"API 요청 실패: {e}")
    
    def download_corp_codes(self, save_json: bool = True) -> Dict[str, Any]:
        """
        고유번호 다운로드 API 호출
        전체 상장회사의 고유번호를 ZIP 파일로 다운로드하고 JSON으로 변환
        
        Args:
            save_json: JSON 파일로 저장 여부
            
        Returns:
            회사 정보 딕셔너리 (corp_code를 키로 하는 딕셔너리)
        """
        url = f"{self.base_url}/corpCode.xml"
        
        params = {
            'crtfc_key': self.api_key
        }
        
        try:
            print("회사 고유번호를 다운로드하는 중...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # ZIP 파일 처리
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # ZIP 파일 내의 XML 파일 읽기
                xml_filename = zip_file.namelist()[0]
                xml_content = zip_file.read(xml_filename).decode('utf-8')
            
            # XML을 파싱하여 회사 정보 추출
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            corp_codes = {}
            corp_list = []
            
            for corp in root.findall('.//list'):
                corp_code = corp.find('corp_code').text if corp.find('corp_code') is not None else ''
                corp_name = corp.find('corp_name').text if corp.find('corp_name') is not None else ''
                stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else ''
                modify_date = corp.find('modify_date').text if corp.find('modify_date') is not None else ''
                
                # 회사 정보 딕셔너리
                corp_info = {
                    'corp_code': corp_code,
                    'corp_name': corp_name,
                    'stock_code': stock_code,
                    'modify_date': modify_date
                }
                
                corp_codes[corp_code] = corp_info
                corp_list.append(corp_info)
            
            print(f"총 {len(corp_list)}개 회사 정보를 다운로드했습니다.")
            
            # JSON 파일로 저장
            if save_json:
                filename = 'corpCodes.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(corp_list, f, ensure_ascii=False, indent=2)
                print(f"회사 정보가 {filename}에 저장되었습니다.")
            
            return corp_codes
            
        except requests.RequestException as e:
            raise Exception(f"회사 코드 다운로드 실패: {e}")
        except Exception as e:
            raise Exception(f"회사 코드 처리 실패: {e}")
    
    def get_financial_statements(self, 
                               corp_code: str,
                               bsns_year: str,
                               reprt_code: str) -> Dict[str, Any]:
        """
        단일회사 주요계정 조회 API 호출
        
        Args:
            corp_code: 고유번호 (8자리)
            bsns_year: 사업연도 (4자리, 2015년 이후)
            reprt_code: 보고서 코드
                       11013: 1분기보고서
                       11012: 반기보고서  
                       11014: 3분기보고서
                       11011: 사업보고서
                       
        Returns:
            재무제표 데이터
        """
        url = f"{self.base_url}/fnlttSinglAcnt.json"
        
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"재무제표 조회 실패: {e}")
    
    def get_multiple_year_financials(self,
                                   corp_code: str,
                                   start_year: int,
                                   end_year: int,
                                   reprt_code: str = '11011') -> Dict[str, Any]:
        """
        여러 연도의 재무제표 데이터 조회
        
        Args:
            corp_code: 고유번호
            start_year: 시작 연도
            end_year: 종료 연도  
            reprt_code: 보고서 코드 (기본값: 사업보고서)
            
        Returns:
            연도별 재무제표 데이터
        """
        all_data = {}
        
        for year in range(start_year, end_year + 1):
            try:
                result = self.get_financial_statements(corp_code, str(year), reprt_code)
                if result['status'] == '000':
                    all_data[str(year)] = result.get('list', [])
                else:
                    print(f"{year}년 데이터 조회 실패: {result['message']}")
                    all_data[str(year)] = []
            except Exception as e:
                print(f"{year}년 데이터 조회 오류: {e}")
                all_data[str(year)] = []
        
        return all_data
    
    def parse_financial_data(self, financial_data: List[Dict]) -> Dict[str, Dict]:
        """
        재무제표 데이터를 구조화된 형태로 파싱
        
        Args:
            financial_data: 원본 재무제표 데이터
            
        Returns:
            구조화된 재무제표 데이터
        """
        parsed_data = {
            'BS': {},  # 재무상태표 (Balance Sheet)
            'IS': {}   # 손익계산서 (Income Statement)  
        }
        
        for item in financial_data:
            sj_div = item.get('sj_div', '')  # 재무제표구분
            account_nm = item.get('account_nm', '')  # 계정명
            thstrm_amount = item.get('thstrm_amount', '0')  # 당기금액
            frmtrm_amount = item.get('frmtrm_amount', '0')  # 전기금액
            
            if sj_div in ['BS', 'IS'] and account_nm:
                if account_nm not in parsed_data[sj_div]:
                    parsed_data[sj_div][account_nm] = {}
                
                # 금액을 숫자로 변환 (쉼표 제거)
                try:
                    current_amount = int(thstrm_amount.replace(',', '')) if thstrm_amount else 0
                    previous_amount = int(frmtrm_amount.replace(',', '')) if frmtrm_amount else 0
                except (ValueError, AttributeError):
                    current_amount = 0
                    previous_amount = 0
                
                parsed_data[sj_div][account_nm] = {
                    'current': current_amount,
                    'previous': previous_amount,
                    'current_formatted': thstrm_amount,
                    'previous_formatted': frmtrm_amount
                }
        
        return parsed_data
    
    def get_key_financial_metrics(self, parsed_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        주요 재무지표 계산
        
        Args:
            parsed_data: 파싱된 재무제표 데이터
            
        Returns:
            주요 재무지표
        """
        bs_data = parsed_data.get('BS', {})
        is_data = parsed_data.get('IS', {})
        
        # 주요 계정 추출 (다양한 표기법 고려)
        def get_amount(data_dict, account_names):
            for name in account_names:
                if name in data_dict:
                    return data_dict[name]['current']
            return 0
        
        # 재무상태표 주요 항목
        total_assets = get_amount(bs_data, ['자산총계', '총자산'])
        total_equity = get_amount(bs_data, ['자본총계', '총자본', '자본금'])
        total_liabilities = get_amount(bs_data, ['부채총계', '총부채'])
        
        # 유동/비유동 자산
        current_assets = get_amount(bs_data, ['유동자산'])
        non_current_assets = get_amount(bs_data, ['비유동자산'])
        
        # 유동/비유동 부채
        current_liabilities = get_amount(bs_data, ['유동부채'])
        non_current_liabilities = get_amount(bs_data, ['비유동부채'])
        
        # 손익계산서 주요 항목  
        revenue = get_amount(is_data, ['매출액', '영업수익', '수익(매출액)'])
        operating_profit = get_amount(is_data, ['영업이익'])
        net_income = get_amount(is_data, ['당기순이익', '순이익'])
        
        # 재무비율 계산
        metrics = {
            'total_assets': total_assets,
            'total_equity': total_equity, 
            'total_liabilities': total_liabilities,
            'current_assets': current_assets,
            'non_current_assets': non_current_assets,
            'current_liabilities': current_liabilities,
            'non_current_liabilities': non_current_liabilities,
            'revenue': revenue,
            'operating_profit': operating_profit,
            'net_income': net_income,
            'debt_ratio': round((total_liabilities / total_assets * 100), 2) if total_assets > 0 else 0,
            'equity_ratio': round((total_equity / total_assets * 100), 2) if total_assets > 0 else 0,
            'operating_margin': round((operating_profit / revenue * 100), 2) if revenue > 0 else 0,
            'net_margin': round((net_income / revenue * 100), 2) if revenue > 0 else 0,
            'roe': round((net_income / total_equity * 100), 2) if total_equity > 0 else 0,
            'current_ratio': round((current_assets / current_liabilities), 2) if current_liabilities > 0 else 0
        }
        
        return metrics
    
    def load_corp_codes(self, filename: str = 'corpCodes.json') -> Dict[str, Any]:
        """
        저장된 회사 코드 JSON 파일을 로드
        
        Args:
            filename: JSON 파일명
            
        Returns:
            회사 정보 딕셔너리
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                corp_list = json.load(f)
            
            # 리스트를 딕셔너리로 변환 (corp_code를 키로 사용)
            corp_codes = {corp['corp_code']: corp for corp in corp_list}
            
            print(f"{filename}에서 {len(corp_codes)}개 회사 정보를 로드했습니다.")
            return corp_codes
            
        except FileNotFoundError:
            print(f"{filename} 파일이 없습니다. download_corp_codes()를 먼저 실행해주세요.")
            return {}
        except Exception as e:
            raise Exception(f"회사 코드 로드 실패: {e}")
    
    def search_company(self, search_term: str, corp_codes: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        회사명으로 회사 정보 검색
        
        Args:
            search_term: 검색할 회사명 (부분 일치)
            corp_codes: 회사 코드 딕셔너리 (없으면 파일에서 로드)
            
        Returns:
            검색된 회사 정보 리스트
        """
        if corp_codes is None:
            corp_codes = self.load_corp_codes()
        
        if not corp_codes:
            return []
        
        # 회사명으로 검색 (대소문자 무시, 부분 일치)
        search_term = search_term.lower()
        results = []
        
        for corp_code, corp_info in corp_codes.items():
            if search_term in corp_info['corp_name'].lower():
                results.append(corp_info)
        
        # 회사명으로 정렬
        results.sort(key=lambda x: x['corp_name'])
        
        return results
    
    def get_all_disclosures(self,
                           corp_code: Optional[str] = None,
                           bgn_de: Optional[str] = None,
                           end_de: Optional[str] = None,
                           **kwargs) -> List[Dict[str, Any]]:
        """
        모든 페이지의 공시 정보를 가져옴
        
        Args:
            corp_code: 고유번호
            bgn_de: 시작일
            end_de: 종료일
            **kwargs: 기타 검색 옵션
            
        Returns:
            모든 공시 정보 리스트
        """
        all_disclosures = []
        page_no = 1
        page_count = 100  # 최대값 사용
        
        while True:
            result = self.search_disclosure(
                corp_code=corp_code,
                bgn_de=bgn_de,
                end_de=end_de,
                page_no=page_no,
                page_count=page_count,
                **kwargs
            )
            
            if result['status'] != '000':
                if result['status'] == '013':  # 조회된 데이터가 없음
                    break
                else:
                    raise Exception(f"API 오류: {result['status']} - {result['message']}")
            
            if 'list' in result and result['list']:
                all_disclosures.extend(result['list'])
                
                # 마지막 페이지인지 확인
                if page_no >= result.get('total_page', 1):
                    break
                    
                page_no += 1
            else:
                break
                
        return all_disclosures
    
    def to_dataframe(self, disclosures: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        공시 정보를 DataFrame으로 변환
        
        Args:
            disclosures: 공시 정보 리스트
            
        Returns:
            DataFrame
        """
        if not disclosures:
            return pd.DataFrame()
            
        df = pd.DataFrame(disclosures)
        
        # 날짜 컬럼 변환
        if 'rcept_dt' in df.columns:
            df['rcept_dt'] = pd.to_datetime(df['rcept_dt'], format='%Y%m%d')
            
        return df
    
    def save_to_excel(self, disclosures: List[Dict[str, Any]], filename: str):
        """
        공시 정보를 Excel 파일로 저장
        
        Args:
            disclosures: 공시 정보 리스트
            filename: 저장할 파일명
        """
        df = self.to_dataframe(disclosures)
        if not df.empty:
            # Excel 파일 저장 (encoding 파라미터 제거)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"데이터가 {filename}에 저장되었습니다. (총 {len(df)}건)")
        else:
            print("저장할 데이터가 없습니다.")
    
    def save_to_csv(self, disclosures: List[Dict[str, Any]], filename: str):
        """
        공시 정보를 CSV 파일로 저장
        
        Args:
            disclosures: 공시 정보 리스트
            filename: 저장할 파일명
        """
        df = self.to_dataframe(disclosures)
        if not df.empty:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"데이터가 {filename}에 저장되었습니다. (총 {len(df)}건)")
        else:
            print("저장할 데이터가 없습니다.")
    
    def save_to_json(self, disclosures: List[Dict[str, Any]], filename: str, indent: int = 2):
        """
        공시 정보를 JSON 파일로 저장
        
        Args:
            disclosures: 공시 정보 리스트
            filename: 저장할 파일명
            indent: JSON 들여쓰기 (기본값: 2)
        """
        if disclosures:
            # 날짜 형식을 문자열로 변환 (JSON 직렬화를 위해)
            json_data = []
            for disclosure in disclosures:
                item = disclosure.copy()
                # 날짜 데이터가 있으면 문자열로 변환
                if 'rcept_dt' in item and hasattr(item['rcept_dt'], 'strftime'):
                    item['rcept_dt'] = item['rcept_dt'].strftime('%Y-%m-%d')
                json_data.append(item)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=indent)
            print(f"데이터가 {filename}에 저장되었습니다. (총 {len(json_data)}건)")
        else:
            print("저장할 데이터가 없습니다.")
    
    def save_data(self, disclosures: List[Dict[str, Any]], filename: str, format_type: str = 'csv'):
        """
        공시 정보를 지정된 형식으로 저장
        
        Args:
            disclosures: 공시 정보 리스트
            filename: 저장할 파일명 (확장자 제외)
            format_type: 저장 형식 ('csv', 'excel', 'json', 'all')
        """
        if not disclosures:
            print("저장할 데이터가 없습니다.")
            return
        
        base_filename = filename.replace('.csv', '').replace('.xlsx', '').replace('.json', '')
        
        if format_type.lower() == 'csv':
            self.save_to_csv(disclosures, f"{base_filename}.csv")
        elif format_type.lower() in ['excel', 'xlsx']:
            self.save_to_excel(disclosures, f"{base_filename}.xlsx")
        elif format_type.lower() == 'json':
            self.save_to_json(disclosures, f"{base_filename}.json")
        elif format_type.lower() == 'all':
            self.save_to_csv(disclosures, f"{base_filename}.csv")
            self.save_to_excel(disclosures, f"{base_filename}.xlsx")
            self.save_to_json(disclosures, f"{base_filename}.json")
        else:
            print(f"지원하지 않는 형식입니다: {format_type}")
            print("지원 형식: 'csv', 'excel', 'json', 'all'")

def get_recent_date_range(days: int = 7) -> tuple:
    """
    최근 며칠간의 날짜 범위를 반환
    
    Args:
        days: 며칠 전부터
        
    Returns:
        (시작일, 종료일) YYYYMMDD 형식
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')

def print_disclosure_summary(disclosures: List[Dict[str, Any]]):
    """
    공시 정보 요약 출력
    
    Args:
        disclosures: 공시 정보 리스트
    """
    if not disclosures:
        print("조회된 공시가 없습니다.")
        return
        
    print(f"\n총 {len(disclosures)}건의 공시가 조회되었습니다.\n")
    
    # 최근 10건 출력
    print("최근 공시 (최대 10건):")
    print("-" * 100)
    print(f"{'접수일자':<12} {'회사명':<20} {'보고서명':<50}")
    print("-" * 100)
    
    for disclosure in disclosures[:10]:
        corp_name = disclosure.get('corp_name', '')[:18] + '..' if len(disclosure.get('corp_name', '')) > 20 else disclosure.get('corp_name', '')
        report_nm = disclosure.get('report_nm', '')[:48] + '..' if len(disclosure.get('report_nm', '')) > 50 else disclosure.get('report_nm', '')
        
        print(f"{disclosure.get('rcept_dt', ''):<12} {corp_name:<20} {report_nm:<50}")

if __name__ == "__main__":
    # 사용 예시
    try:
        # API 인스턴스 생성
        dart = DartAPI()
        
        # 최근 7일간의 유가증권시장 공시 검색
        bgn_de, end_de = get_recent_date_range(7)
        
        print(f"DART 공시검색: {bgn_de} ~ {end_de}")
        print("유가증권시장 상장회사 공시를 검색합니다...")
        
        disclosures = dart.get_all_disclosures(
            bgn_de=bgn_de,
            end_de=end_de,
            corp_cls='Y'  # 유가증권시장
        )
        
        # 결과 출력
        print_disclosure_summary(disclosures)
        
        # 파일로 저장 (CSV와 JSON 형식)
        if disclosures:
            filename = f"dart_disclosures_{bgn_de}_{end_de}"
            dart.save_data(disclosures, filename, 'csv')  # CSV로 저장
            dart.save_data(disclosures, filename, 'json')  # JSON으로도 저장
            
    except Exception as e:
        print(f"오류 발생: {e}")
        print("API 키가 올바르게 설정되었는지 확인해주세요.")
