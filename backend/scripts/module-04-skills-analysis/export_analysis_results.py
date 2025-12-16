# Location: backend/scripts/module-04-skills-analysis/export_analysis_results.py
"""
Export Analysis Results
Module #4: Skills Demand Analysis - Export Tool

Export analysis results to multiple formats:
- CSV (frequency, co-occurrence, categories)
- JSON (complete analysis)
- Excel (multiple sheets)

Run: python scripts/module-04-skills-analysis/export_analysis_results.py

Author: Arya
Date: 2025-12-16
Project: Job Market Intelligence Platform
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import os
from dotenv import load_dotenv

try:
    import pandas as pd
except ImportError:
    print("❌ Missing pandas. Install with: pip install pandas")
    sys.exit(1)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.analytics.skill_demand import SkillDemandService

# Load environment
load_dotenv()

OUTPUT_DIR = Path("outputs/module-04-exports")


class AnalysisExporter:
    """Export analysis results to various formats"""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """Initialize exporter"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def export_to_csv(self, results: dict) -> list:
        """Export analysis results to CSV files"""
        
        print(f"\n📄 Exporting to CSV...")
        
        csv_files = []
        
        # 1. Frequency data
        frequency_df = pd.DataFrame(results['frequency']['skills'])
        freq_file = self.output_dir / f"skills_frequency_{self.timestamp}.csv"
        frequency_df.to_csv(freq_file, index=False, encoding='utf-8')
        csv_files.append(freq_file)
        print(f"   ✅ {freq_file.name}")
        
        # 2. Co-occurrence data
        if results['cooccurrence']['pairs']:
            cooccur_df = pd.DataFrame(results['cooccurrence']['pairs'])
            cooccur_file = self.output_dir / f"skills_cooccurrence_{self.timestamp}.csv"
            cooccur_df.to_csv(cooccur_file, index=False, encoding='utf-8')
            csv_files.append(cooccur_file)
            print(f"   ✅ {cooccur_file.name}")
        
        # 3. Category distribution
        category_df = pd.DataFrame(results['category_distribution']['categories'])
        cat_file = self.output_dir / f"category_distribution_{self.timestamp}.csv"
        category_df.to_csv(cat_file, index=False, encoding='utf-8')
        csv_files.append(cat_file)
        print(f"   ✅ {cat_file.name}")
        
        # 4. Top skills by category
        top_by_category = []
        for skill in results['frequency']['skills'][:100]:
            top_by_category.append({
                'rank': skill['rank'],
                'skill': skill['skill'],
                'category': skill['category'],
                'demand_count': skill['demand_count'],
                'percentage': skill['percentage']
            })
        
        top_cat_df = pd.DataFrame(top_by_category)
        top_cat_file = self.output_dir / f"top_skills_categorized_{self.timestamp}.csv"
        top_cat_df.to_csv(top_cat_file, index=False, encoding='utf-8')
        csv_files.append(top_cat_file)
        print(f"   ✅ {top_cat_file.name}")
        
        return csv_files
    
    def export_to_json(self, results: dict) -> Path:
        """Export complete analysis to JSON"""
        
        print(f"\n📄 Exporting to JSON...")
        
        json_file = self.output_dir / f"complete_analysis_{self.timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ {json_file.name}")
        return json_file
    
    def export_to_excel(self, results: dict) -> Path:
        """Export to Excel with multiple sheets"""
        
        print(f"\n📄 Exporting to Excel...")
        
        try:
            excel_file = self.output_dir / f"skills_analysis_{self.timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Sheet 1: Summary
                summary_data = {
                    'Metric': [
                        'Total Jobs Analyzed',
                        'Total Unique Skills',
                        'Total Categories',
                        'Avg Skills per Job',
                        'Analysis Date'
                    ],
                    'Value': [
                        results['summary']['total_jobs_analyzed'],
                        results['summary']['total_unique_skills'],
                        results['summary']['total_categories'],
                        results['summary']['avg_skills_per_job'],
                        results['summary']['analysis_timestamp']
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Sheet 2: Frequency
                frequency_df = pd.DataFrame(results['frequency']['skills'])
                frequency_df.to_excel(writer, sheet_name='Skill Frequency', index=False)
                
                # Sheet 3: Categories
                category_df = pd.DataFrame(results['category_distribution']['categories'])
                category_df.to_excel(writer, sheet_name='Categories', index=False)
                
                # Sheet 4: Co-occurrence
                if results['cooccurrence']['pairs']:
                    cooccur_df = pd.DataFrame(results['cooccurrence']['pairs'])
                    cooccur_df.to_excel(writer, sheet_name='Co-occurrence', index=False)
                
                # Sheet 5: Top 3 Skills
                top3_data = {
                    'Rank': [1, 2, 3],
                    'Skill': results['summary']['top_3_skills']
                }
                pd.DataFrame(top3_data).to_excel(writer, sheet_name='Top 3', index=False)
            
            print(f"   ✅ {excel_file.name}")
            return excel_file
        
        except ImportError:
            print("   ⚠️  openpyxl not installed, skipping Excel export")
            print("   Install with: pip install openpyxl")
            return None
    
    def export_summary_text(self, results: dict) -> Path:
        """Export human-readable summary"""
        
        print(f"\n📄 Exporting summary text...")
        
        summary_file = self.output_dir / f"analysis_summary_{self.timestamp}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SKILLS DEMAND ANALYSIS SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            
            # Summary stats
            f.write("📊 OVERVIEW\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Jobs Analyzed:    {results['summary']['total_jobs_analyzed']:,}\n")
            f.write(f"Total Unique Skills:    {results['summary']['total_unique_skills']:,}\n")
            f.write(f"Total Categories:       {results['summary']['total_categories']}\n")
            f.write(f"Avg Skills per Job:     {results['summary']['avg_skills_per_job']}\n")
            f.write(f"Analysis Date:          {results['summary']['analysis_timestamp']}\n\n")
            
            # Top skills
            f.write("🏆 TOP 20 MOST DEMANDED SKILLS\n")
            f.write("-" * 70 + "\n")
            for skill in results['frequency']['skills'][:20]:
                f.write(f"{skill['rank']:2}. {skill['skill']:<30} {skill['demand_count']:>6,} jobs ({skill['percentage']:>5.1f}%)\n")
            f.write("\n")
            
            # Categories
            f.write("📂 CATEGORY DISTRIBUTION\n")
            f.write("-" * 70 + "\n")
            for cat in results['category_distribution']['categories']:
                f.write(f"{cat['category']:<25} {cat['unique_skills']:>3} skills, {cat['total_demand']:>6,} total\n")
            f.write("\n")
            
            # Top pairs
            if results['cooccurrence']['pairs']:
                f.write("🔗 TOP 10 SKILL PAIRS\n")
                f.write("-" * 70 + "\n")
                for i, pair in enumerate(results['cooccurrence']['pairs'][:10], 1):
                    f.write(f"{i:2}. {pair['skill_1']:<20} + {pair['skill_2']:<20} ({pair['cooccurrence_count']:>4} jobs)\n")
                f.write("\n")
            
            f.write("=" * 70 + "\n")
        
        print(f"   ✅ {summary_file.name}")
        return summary_file


def export_all(limit: int = None):
    """Run analysis and export to all formats"""
    
    print("\n" + "=" * 70)
    print("EXPORT ANALYSIS RESULTS - MODULE #4")
    print("=" * 70)
    
    # Database connection
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
    )
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Run analysis
        print(f"\n🔍 Running analysis...")
        if limit:
            print(f"   Sample: {limit:,} jobs")
        else:
            print(f"   Full dataset: ALL jobs")
        
        service = SkillDemandService(db)
        results = service.run_complete_analysis(limit=limit, top_n=100, min_cooccurrence=5)
        
        if 'error' in results:
            print(f"\n❌ Error: {results['error']}")
            return
        
        print(f"   ✅ Analyzed {results['summary']['total_jobs_analyzed']:,} jobs")
        
        # Export
        exporter = AnalysisExporter()
        
        csv_files = exporter.export_to_csv(results)
        json_file = exporter.export_to_json(results)
        excel_file = exporter.export_to_excel(results)
        summary_file = exporter.export_summary_text(results)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ EXPORT COMPLETE")
        print("=" * 70)
        print(f"\n📁 Output directory: {exporter.output_dir.absolute()}")
        print(f"\nExported files:")
        for f in csv_files:
            print(f"   📄 {f.name}")
        print(f"   📄 {json_file.name}")
        if excel_file:
            print(f"   📄 {excel_file.name}")
        print(f"   📄 {summary_file.name}")
        
        print(f"\n💡 Total files: {len(csv_files) + 2 + (1 if excel_file else 0)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export skills analysis results")
    parser.add_argument('--limit', type=int, default=None, help='Limit number of jobs')
    
    args = parser.parse_args()
    
    export_all(limit=args.limit)