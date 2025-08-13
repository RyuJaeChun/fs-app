"""
회사 코드 데이터베이스 관리 모듈
corpCodes.json을 SQLite 데이터베이스로 변환하고 검색 기능 제공
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Company:
    """회사 정보 데이터 클래스"""
    corp_code: str
    corp_name: str
    stock_code: str
    modify_date: str

class CompanyDatabase:
    """회사 코드 데이터베이스 클래스"""
    
    def __init__(self, db_path: str = "companies.db"):
        """
        데이터베이스 초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    corp_code TEXT PRIMARY KEY,
                    corp_name TEXT NOT NULL,
                    stock_code TEXT,
                    modify_date TEXT,
                    UNIQUE(corp_code)
                )
            ''')
            
            # 검색 성능 향상을 위한 인덱스 생성
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_corp_name 
                ON companies(corp_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_stock_code 
                ON companies(stock_code)
            ''')
            
            conn.commit()
    
    def load_from_json(self, json_path: str = "corpCodes.json"):
        """
        JSON 파일에서 회사 데이터를 로드하여 데이터베이스에 저장
        
        Args:
            json_path: corpCodes.json 파일 경로
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"{json_path} 파일이 없습니다. 먼저 회사 코드를 다운로드해주세요.")
        
        print(f"{json_path}에서 회사 데이터를 로드합니다...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            companies_data = json.load(f)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 데이터 삭제
            cursor.execute("DELETE FROM companies")
            
            # 새 데이터 삽입
            for company in companies_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO companies 
                    (corp_code, corp_name, stock_code, modify_date)
                    VALUES (?, ?, ?, ?)
                ''', (
                    company.get('corp_code', ''),
                    company.get('corp_name', ''),
                    company.get('stock_code', ''),
                    company.get('modify_date', '')
                ))
            
            conn.commit()
        
        # 로드된 데이터 통계
        total_count = self.get_company_count()
        listed_count = self.get_listed_company_count()
        
        print(f"데이터베이스 로드 완료:")
        print(f"  - 전체 회사: {total_count:,}개")
        print(f"  - 상장회사: {listed_count:,}개")
        print(f"  - 비상장회사: {total_count - listed_count:,}개")
    
    def search_companies(self, search_term: str, limit: int = 50) -> List[Company]:
        """
        회사명으로 회사 검색 (부분 일치)
        
        Args:
            search_term: 검색어
            limit: 최대 검색 결과 수
            
        Returns:
            검색된 회사 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT corp_code, corp_name, stock_code, modify_date
                FROM companies
                WHERE corp_name LIKE ?
                ORDER BY 
                    CASE WHEN corp_name = ? THEN 1 ELSE 2 END,
                    LENGTH(corp_name),
                    corp_name
                LIMIT ?
            ''', (f'%{search_term}%', search_term, limit))
            
            results = cursor.fetchall()
            
            return [Company(
                corp_code=row[0],
                corp_name=row[1],
                stock_code=row[2],
                modify_date=row[3]
            ) for row in results]
    
    def get_company_by_code(self, corp_code: str) -> Optional[Company]:
        """
        고유번호로 회사 정보 조회
        
        Args:
            corp_code: 회사 고유번호
            
        Returns:
            회사 정보 또는 None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT corp_code, corp_name, stock_code, modify_date
                FROM companies
                WHERE corp_code = ?
            ''', (corp_code,))
            
            result = cursor.fetchone()
            
            if result:
                return Company(
                    corp_code=result[0],
                    corp_name=result[1],
                    stock_code=result[2],
                    modify_date=result[3]
                )
            return None
    
    def get_company_by_name(self, corp_name: str) -> Optional[Company]:
        """
        회사명으로 정확한 회사 정보 조회
        
        Args:
            corp_name: 회사명
            
        Returns:
            회사 정보 또는 None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT corp_code, corp_name, stock_code, modify_date
                FROM companies
                WHERE corp_name = ?
            ''', (corp_name,))
            
            result = cursor.fetchone()
            
            if result:
                return Company(
                    corp_code=result[0],
                    corp_name=result[1],
                    stock_code=result[2],
                    modify_date=result[3]
                )
            return None
    
    def get_listed_companies(self, limit: int = 1000) -> List[Company]:
        """
        상장회사 목록 조회
        
        Args:
            limit: 최대 조회 수
            
        Returns:
            상장회사 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT corp_code, corp_name, stock_code, modify_date
                FROM companies
                WHERE stock_code != '' AND stock_code IS NOT NULL
                ORDER BY corp_name
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            return [Company(
                corp_code=row[0],
                corp_name=row[1],
                stock_code=row[2],
                modify_date=row[3]
            ) for row in results]
    
    def get_company_count(self) -> int:
        """전체 회사 수 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM companies")
            return cursor.fetchone()[0]
    
    def get_listed_company_count(self) -> int:
        """상장회사 수 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM companies
                WHERE stock_code != '' AND stock_code IS NOT NULL
            ''')
            return cursor.fetchone()[0]
    
    def get_popular_companies(self, limit: int = 20) -> List[Company]:
        """
        인기 회사 목록 (주요 대기업들)
        
        Args:
            limit: 최대 조회 수
            
        Returns:
            인기 회사 리스트
        """
        popular_names = [
            '삼성전자', 'SK하이닉스', 'NAVER', '카카오', 'LG에너지솔루션',
            'LG화학', '현대자동차', '기아', 'POSCO홀딩스', 'KB금융',
            '셀트리온', '삼성바이오로직스', '한국전력', '삼성물산', 'LG전자',
            '현대모비스', 'SK텔레콤', 'KT&G', '아모레퍼시픽', '하나금융지주'
        ]
        
        companies = []
        for name in popular_names:
            company = self.get_company_by_name(name)
            if company:
                companies.append(company)
            if len(companies) >= limit:
                break
        
        return companies

def setup_database():
    """데이터베이스 설정 및 초기화"""
    db = CompanyDatabase()
    
    # corpCodes.json이 있으면 로드
    if os.path.exists("corpCodes.json"):
        db.load_from_json()
        print("✅ 회사 데이터베이스가 성공적으로 설정되었습니다.")
    else:
        print("❌ corpCodes.json 파일이 없습니다.")
        print("먼저 다음 명령을 실행해주세요:")
        print("python corp_codes_example.py")
    
    return db

if __name__ == "__main__":
    # 데이터베이스 설정 및 테스트
    try:
        db = setup_database()
        
        # 검색 테스트
        print("\n=== 검색 테스트 ===")
        test_searches = ["삼성", "LG", "현대"]
        
        for term in test_searches:
            results = db.search_companies(term, limit=5)
            print(f"\n'{term}' 검색 결과:")
            for company in results:
                stock_info = f" ({company.stock_code})" if company.stock_code else " (비상장)"
                print(f"  - {company.corp_name}{stock_info} - {company.corp_code}")
        
        # 인기 회사 테스트
        print("\n=== 인기 회사 ===")
        popular = db.get_popular_companies(10)
        for company in popular:
            print(f"  - {company.corp_name} ({company.stock_code}) - {company.corp_code}")
        
    except Exception as e:
        print(f"오류 발생: {e}")

