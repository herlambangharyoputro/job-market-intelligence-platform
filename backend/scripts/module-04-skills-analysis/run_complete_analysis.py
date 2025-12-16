# Location: backend/scripts/module-04-skills-analysis/run_complete_analysis.py
"""
Complete Skills Demand Analysis Runner
Module #4: Skills Demand Analysis - One-Click Runner

Runs complete analysis pipeline:
1. Skills demand analysis
2. Generate visualizations
3. Export to multiple formats
4. Create summary report

Run: python scripts/module-04-skills-analysis/run_complete_analysis.py

Options:
  --limit N       Analyze only N jobs (for testing)
  --no-viz        Skip visualization generation
  --no-export     Skip export generation

Author: Arya
Date: 2025-12-16
Project: Job Market Intelligence Platform
"""

import sys
from pathlib import Path
from datetime import datetime
import time

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


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)


def print_section(text):
    """Print section header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}")


def print_step(step_num, total_steps, text):
    """Print step indicator"""
    print(f"\n[{step_num}/{total_steps}] {text}")


def run_complete_analysis(
    limit: int = None,
    generate_viz: bool = True,
    generate_exports: bool = True
):
    """
    Run complete skills demand analysis pipeline
    
    Args:
        limit: Number of jobs to analyze (None = all)
        generate_viz: Generate visualizations
        generate_exports: Export to files
    """
    
    start_time = time.time()
    
    print_header("MODULE #4: SKILLS DEMAND ANALYSIS")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if limit:
        print(f"Mode: SAMPLE ({limit:,} jobs)")
    else:
        print(f"Mode: FULL DATASET (all jobs)")
    
    # Database connection
    print("\n🔌 Connecting to database...")
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
    )
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    results = None
    
    try:
        # ============================================================
        # STEP 1: Run Analysis
        # ============================================================
        total_steps = 3
        print_step(1, total_steps, "ANALYZING SKILLS DEMAND")
        print("-" * 70)
        
        print("   🔍 Extracting skills from jobs...")
        service = SkillDemandService(db)
        
        print("   📊 Running frequency analysis...")
        print("   🔗 Calculating co-occurrence patterns...")
        print("   📂 Analyzing category distribution...")
        
        results = service.run_complete_analysis(
            limit=limit,
            top_n=100,
            min_cooccurrence=5
        )
        
        if 'error' in results:
            print(f"\n   ❌ Error: {results['error']}")
            return False
        
        summary = results['summary']
        
        print(f"\n   ✅ Analysis complete!")
        print(f"      • Jobs analyzed: {summary['total_jobs_analyzed']:,}")
        print(f"      • Unique skills: {summary['total_unique_skills']:,}")
        print(f"      • Categories: {summary['total_categories']}")
        print(f"      • Avg skills/job: {summary['avg_skills_per_job']}")
        print(f"      • Top 3 skills: {', '.join(summary['top_3_skills'][:3])}")
        
        # ============================================================
        # STEP 2: Generate Visualizations
        # ============================================================
        viz_files = []
        
        if generate_viz:
            print_step(2, total_steps, "GENERATING VISUALIZATIONS")
            print("-" * 70)
            
            try:
                # Import visualization module
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                # Import generator
                from generate_visualizations import VisualizationGenerator
                
                # Convert to DataFrame
                frequency_df = pd.DataFrame(results['frequency']['skills'])
                
                # Initialize generator
                viz_dir = Path("outputs/module-04-visualizations")
                generator = VisualizationGenerator(viz_dir)
                
                print("   📊 Creating charts...")
                
                # Generate all visualizations
                viz_files.append(generator.create_top_skills_bar_chart(frequency_df, top_n=30))
                viz_files.append(generator.create_category_pie_chart(results['category_distribution']))
                viz_files.append(generator.create_category_bar_chart(results['category_distribution']))
                
                heatmap = generator.create_cooccurrence_heatmap(results['cooccurrence'], top_n=20)
                if heatmap:
                    viz_files.append(heatmap)
                
                pairs = generator.create_top_pairs_chart(results['cooccurrence'], top_n=15)
                if pairs:
                    viz_files.append(pairs)
                
                viz_files.append(generator.create_summary_dashboard(
                    results['summary'],
                    frequency_df,
                    results['category_distribution']
                ))
                
                print(f"\n   ✅ Generated {len([v for v in viz_files if v])} visualizations")
                for viz in viz_files:
                    if viz:
                        print(f"      • {viz.name}")
            
            except ImportError as e:
                print(f"\n   ⚠️  Skipping visualizations: {e}")
                print("      Install with: pip install matplotlib seaborn")
        
        else:
            print_step(2, total_steps, "SKIPPING VISUALIZATIONS (--no-viz)")
        
        # ============================================================
        # STEP 3: Export Results
        # ============================================================
        export_files = []
        
        if generate_exports:
            print_step(3, total_steps, "EXPORTING RESULTS")
            print("-" * 70)
            
            try:
                # Import exporter
                from export_analysis_results import AnalysisExporter
                
                # Initialize exporter
                export_dir = Path("outputs/module-04-exports")
                exporter = AnalysisExporter(export_dir)
                
                print("   💾 Exporting to files...")
                
                # Export to all formats
                csv_files = exporter.export_to_csv(results)
                json_file = exporter.export_to_json(results)
                excel_file = exporter.export_to_excel(results)
                summary_file = exporter.export_summary_text(results)
                
                export_files.extend(csv_files)
                export_files.append(json_file)
                if excel_file:
                    export_files.append(excel_file)
                export_files.append(summary_file)
                
                print(f"\n   ✅ Exported {len(export_files)} files")
                for exp_file in export_files[:5]:  # Show first 5
                    print(f"      • {exp_file.name}")
                if len(export_files) > 5:
                    print(f"      ... and {len(export_files) - 5} more")
            
            except Exception as e:
                print(f"\n   ⚠️  Export error: {e}")
        
        else:
            print_step(3, total_steps, "SKIPPING EXPORTS (--no-export)")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        elapsed = time.time() - start_time
        
        print_header("✅ ANALYSIS COMPLETE")
        
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
        print(f"\n📊 Analysis Summary:")
        print(f"   • Jobs analyzed: {summary['total_jobs_analyzed']:,}")
        print(f"   • Unique skills found: {summary['total_unique_skills']:,}")
        print(f"   • Skills per job (avg): {summary['avg_skills_per_job']}")
        
        if viz_files:
            print(f"\n📈 Visualizations: {len([v for v in viz_files if v])} charts created")
        
        if export_files:
            print(f"\n💾 Exports: {len(export_files)} files saved")
        
        print(f"\n📁 Output locations:")
        if viz_files and viz_files[0]:
            print(f"   • Visualizations: {viz_files[0].parent}")
        if export_files:
            print(f"   • Exports: {export_files[0].parent}")
        
        print(f"\n🎯 Top 3 Most Demanded Skills:")
        for i, skill in enumerate(summary['top_3_skills'][:3], 1):
            # Get details
            skill_details = next((s for s in results['frequency']['skills'] if s['skill'] == skill), None)
            if skill_details:
                print(f"   {i}. {skill} - {skill_details['demand_count']:,} jobs ({skill_details['percentage']:.1f}%)")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review visualizations in outputs/module-04-visualizations/")
        print(f"   2. Check exports in outputs/module-04-exports/")
        print(f"   3. Share insights with stakeholders")
        print(f"   4. Upload to HuggingFace for portfolio")
        
        print("\n" + "=" * 70)
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run complete skills demand analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis on all jobs
  python run_complete_analysis.py
  
  # Sample analysis (1000 jobs)
  python run_complete_analysis.py --limit 1000
  
  # Skip visualizations
  python run_complete_analysis.py --no-viz
  
  # Skip exports
  python run_complete_analysis.py --no-export
  
  # Quick test (100 jobs, no viz, no export)
  python run_complete_analysis.py --limit 100 --no-viz --no-export
        """
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of jobs to analyze (None = all jobs)'
    )
    
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip visualization generation'
    )
    
    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip file exports'
    )
    
    args = parser.parse_args()
    
    success = run_complete_analysis(
        limit=args.limit,
        generate_viz=not args.no_viz,
        generate_exports=not args.no_export
    )
    
    sys.exit(0 if success else 1)