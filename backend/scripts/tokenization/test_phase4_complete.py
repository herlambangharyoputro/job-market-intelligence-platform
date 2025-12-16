"""
Phase 4 Testing Suite
Tests tokenization storage and performance

Tests:
1. Database schema verification
2. Storage functionality
3. Query performance
4. Data quality
5. Performance benchmarks

Usage:
    python scripts/test_phase4_complete.py
"""

import sys
import os
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import time
import json
from sqlalchemy import text
from app.database import SessionLocal
from app.services.preprocessing.tokenizers import (
    JobTitleTokenizerEnhanced,
    SkillTokenizer,
    LocationTokenizer,
)


class Phase4Tester:
    """Comprehensive Phase 4 testing"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.results = {
            'schema': False,
            'storage': False,
            'queries': False,
            'quality': False,
            'performance': False
        }
    
    def test_schema(self):
        """Test 1: Verify database schema"""
        print("=" * 70)
        print("TEST 1: DATABASE SCHEMA")
        print("=" * 70)
        print()
        
        try:
            # Check columns exist
            query = text("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'jobs'
                AND COLUMN_NAME IN ('tokens', 'is_tokenized', 'tokenized_at')
            """)
            
            columns = self.db.execute(query).fetchall()
            
            if len(columns) == 3:
                print("✅ All required columns exist:")
                for col in columns:
                    print(f"   - {col[0]} ({col[1]})")
                print()
                self.results['schema'] = True
            else:
                print("❌ Missing columns!")
                print(f"   Found: {len(columns)}/3 columns")
                print()
                return False
            
            # Check indexes
            query = text("""
                SELECT INDEX_NAME
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_NAME = 'jobs'
                AND INDEX_NAME LIKE 'idx_token%'
            """)
            
            indexes = self.db.execute(query).fetchall()
            print(f"✅ Indexes found: {len(indexes)}")
            for idx in indexes:
                print(f"   - {idx[0]}")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Schema test failed: {e}")
            print()
            return False
    
    def test_storage(self):
        """Test 2: Test storage functionality"""
        print("=" * 70)
        print("TEST 2: STORAGE FUNCTIONALITY")
        print("=" * 70)
        print()
        
        try:
            # Get one job
            query = text("SELECT id, judul, level, keahlian FROM jobs LIMIT 1")
            job = self.db.execute(query).fetchone()
            
            if not job:
                print("❌ No jobs in database!")
                return False
            
            print(f"Testing with job {job.id}: {job.judul}")
            print()
            
            # Tokenize
            title_tokenizer = JobTitleTokenizerEnhanced()
            skill_tokenizer = SkillTokenizer()
            
            title_result = title_tokenizer.tokenize_with_reconciliation(job.judul, job.level)
            skill_result = skill_tokenizer.tokenize(job.keahlian) if job.keahlian else None
            
            # Prepare compact tokens
            compact = {
                'title': {
                    'level': title_result.get('level'),
                    'confidence': title_result['level_reconciliation']['confidence']
                },
                'skills': {
                    'count': skill_result.get('total_count', 0) if skill_result else 0
                }
            }
            
            # Save
            update_query = text("""
                UPDATE jobs 
                SET is_tokenized = TRUE,
                    tokens = :tokens,
                    tokenized_at = NOW()
                WHERE id = :job_id
            """)
            
            self.db.execute(update_query, {
                'job_id': job.id,
                'tokens': json.dumps(compact)
            })
            self.db.commit()
            
            print("✅ Token saved successfully!")
            print()
            
            # Verify
            verify_query = text("""
                SELECT is_tokenized, tokens, tokenized_at
                FROM jobs
                WHERE id = :job_id
            """)
            
            result = self.db.execute(verify_query, {'job_id': job.id}).fetchone()
            
            if result.is_tokenized and result.tokens:
                print("✅ Token verified in database:")
                tokens = json.loads(result.tokens)
                print(f"   Level: {tokens.get('title', {}).get('level')}")
                print(f"   Skills: {tokens.get('skills', {}).get('count')}")
                print(f"   Tokenized at: {result.tokenized_at}")
                print()
                self.results['storage'] = True
                return True
            else:
                print("❌ Token not found in database!")
                return False
                
        except Exception as e:
            print(f"❌ Storage test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_queries(self):
        """Test 3: Test JSON queries"""
        print("=" * 70)
        print("TEST 3: JSON QUERY PERFORMANCE")
        print("=" * 70)
        print()
        
        try:
            # Query 1: Count tokenized jobs
            start = time.time()
            query = text("SELECT COUNT(*) FROM jobs WHERE is_tokenized = TRUE")
            count = self.db.execute(query).scalar()
            time1 = (time.time() - start) * 1000
            
            print(f"✅ Query 1: Count tokenized jobs")
            print(f"   Result: {count} jobs")
            print(f"   Time: {time1:.2f}ms")
            print()
            
            if count == 0:
                print("⚠️  No tokenized jobs yet - run batch processing first")
                print()
                return False
            
            # Query 2: Extract level from JSON
            start = time.time()
            query = text("""
                SELECT id, JSON_EXTRACT(tokens, '$.title.level') as level
                FROM jobs
                WHERE is_tokenized = TRUE
                LIMIT 5
            """)
            results = self.db.execute(query).fetchall()
            time2 = (time.time() - start) * 1000
            
            print(f"✅ Query 2: Extract JSON field")
            print(f"   Results: {len(results)} rows")
            print(f"   Time: {time2:.2f}ms")
            for r in results[:3]:
                print(f"   - Job {r.id}: {r.level}")
            print()
            
            # Query 3: Filter by JSON field
            start = time.time()
            query = text("""
                SELECT COUNT(*)
                FROM jobs
                WHERE JSON_EXTRACT(tokens, '$.skills.count') > 0
            """)
            count = self.db.execute(query).scalar()
            time3 = (time.time() - start) * 1000
            
            print(f"✅ Query 3: Filter by JSON field")
            print(f"   Jobs with skills: {count}")
            print(f"   Time: {time3:.2f}ms")
            print()
            
            self.results['queries'] = True
            return True
            
        except Exception as e:
            print(f"❌ Query test failed: {e}")
            return False
    
    def test_quality(self):
        """Test 4: Data quality checks"""
        print("=" * 70)
        print("TEST 4: DATA QUALITY")
        print("=" * 70)
        print()
        
        try:
            # Check completeness
            query = text("""
                SELECT 
                    AVG(JSON_EXTRACT(tokens, '$.stats.completeness')) as avg_completeness,
                    MIN(JSON_EXTRACT(tokens, '$.stats.completeness')) as min_completeness,
                    MAX(JSON_EXTRACT(tokens, '$.stats.completeness')) as max_completeness
                FROM jobs
                WHERE is_tokenized = TRUE
            """)
            
            result = self.db.execute(query).fetchone()
            
            if result.avg_completeness:
                print("✅ Completeness Statistics:")
                print(f"   Average: {float(result.avg_completeness):.2%}")
                print(f"   Minimum: {float(result.min_completeness):.2%}")
                print(f"   Maximum: {float(result.max_completeness):.2%}")
                print()
                
                if float(result.avg_completeness) >= 0.60:
                    print("✅ Quality PASSED (avg >= 60%)")
                    self.results['quality'] = True
                else:
                    print("⚠️  Quality WARNING (avg < 60%)")
            else:
                print("⚠️  No quality data available")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Quality test failed: {e}")
            return False
    
    def test_performance(self):
        """Test 5: Performance benchmarks"""
        print("=" * 70)
        print("TEST 5: PERFORMANCE BENCHMARKS")
        print("=" * 70)
        print()
        
        try:
            from app.services.preprocessing.tokenizers import JobTitleTokenizerEnhanced
            
            tokenizer = JobTitleTokenizerEnhanced()
            
            # Test data
            test_titles = [
                "Senior Full Stack Developer - Jakarta",
                "Junior Backend Engineer",
                "Lead Data Scientist (Machine Learning)",
                "Manager IT Infrastructure",
                "Frontend Developer React",
            ] * 20  # 100 total
            
            print("Benchmarking tokenization speed...")
            print(f"Test size: {len(test_titles)} job titles")
            print()
            
            start = time.time()
            for title in test_titles:
                tokenizer.tokenize_with_reconciliation(title, "mid")
            duration = time.time() - start
            
            speed = len(test_titles) / duration
            
            print(f"✅ Performance Results:")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Speed: {speed:.2f} jobs/second")
            print()
            
            if speed >= 30:
                print("✅ Performance EXCELLENT (>30 jobs/sec)")
                self.results['performance'] = True
            elif speed >= 20:
                print("✅ Performance GOOD (>20 jobs/sec)")
                self.results['performance'] = True
            else:
                print("⚠️  Performance SLOW (<20 jobs/sec)")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("=" * 70)
        print("PHASE 4: TOKENIZATION TESTING SUITE")
        print("=" * 70)
        print("\n")
        
        # Run tests
        self.test_schema()
        self.test_storage()
        self.test_queries()
        self.test_quality()
        self.test_performance()
        
        # Summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print()
        
        passed = sum(self.results.values())
        total = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")
        
        print()
        print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        print()
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Phase 4 implementation complete and verified!")
        elif passed >= total * 0.8:
            print("⚠️  MOSTLY PASSED - Some issues to fix")
        else:
            print("❌ FAILED - Major issues detected")
        
        print()
        print("=" * 70)
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


if __name__ == "__main__":
    tester = Phase4Tester()
    tester.run_all_tests()
