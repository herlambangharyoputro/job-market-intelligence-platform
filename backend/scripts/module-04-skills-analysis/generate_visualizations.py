# Location: backend/scripts/module-04-skills-analysis/generate_visualizations.py
"""
Generate Visualizations for Skills Demand Analysis
Module #4: Skills Demand Analysis - Visualization Tool

Creates professional charts and graphs from analysis results:
- Bar charts (top skills)
- Pie charts (category distribution)
- Heatmaps (co-occurrence matrix)
- Line charts (trends over time)

Run: python scripts/module-04-skills-analysis/generate_visualizations.py

Author: Arya
Date: 2025-12-16
Project: Job Market Intelligence Platform
"""

import sys
from pathlib import Path
from datetime import datetime

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import os
from dotenv import load_dotenv

# Check and install required packages
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nInstall with:")
    print("  pip install matplotlib seaborn pandas numpy")
    sys.exit(1)

from sqlalchemy import create_engine
from app.services.analytics.skill_demand import SkillDemandService, get_skills_demand_report

# Load environment
load_dotenv()

# Configuration
OUTPUT_DIR = Path("outputs/module-04-visualizations")
DPI = 300
FIGURE_SIZE = (12, 8)
COLOR_PALETTE = "husl"

# Seaborn style
sns.set_style("whitegrid")
sns.set_palette(COLOR_PALETTE)


class VisualizationGenerator:
    """Generate visualizations for skills demand analysis"""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """Initialize generator with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def create_top_skills_bar_chart(
        self,
        frequency_data: pd.DataFrame,
        top_n: int = 30,
        filename: str = "top_skills_bar_chart.png"
    ):
        """
        Create horizontal bar chart of top N skills
        """
        print(f"\n📊 Creating top {top_n} skills bar chart...")
        
        # Get top N skills
        top_skills = frequency_data.head(top_n)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.3)))
        
        # Create horizontal bar chart
        bars = ax.barh(
            range(len(top_skills)),
            top_skills['demand_count'],
            color=sns.color_palette(COLOR_PALETTE, len(top_skills))
        )
        
        # Customize
        ax.set_yticks(range(len(top_skills)))
        ax.set_yticklabels(top_skills['skill'])
        ax.invert_yaxis()  # Highest at top
        ax.set_xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Most Demanded Skills', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels
        for i, (idx, row) in enumerate(top_skills.iterrows()):
            ax.text(
                row['demand_count'] + max(top_skills['demand_count']) * 0.01,
                i,
                f"{row['demand_count']:,} ({row['percentage']:.1f}%)",
                va='center',
                fontsize=9
            )
        
        # Grid
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path
    
    def create_category_pie_chart(
        self,
        category_data: dict,
        filename: str = "skills_category_distribution.png"
    ):
        """
        Create pie chart of skills distribution by category
        """
        print(f"\n🥧 Creating category distribution pie chart...")
        
        categories = category_data['categories']
        
        # Prepare data
        labels = [cat['category'].replace('_', ' ').title() for cat in categories]
        sizes = [cat['total_demand'] for cat in categories]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create pie chart
        colors = sns.color_palette(COLOR_PALETTE, len(labels))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Skills Distribution by Category', fontsize=14, fontweight='bold', pad=20)
        
        # Add legend with counts
        legend_labels = [
            f"{label}: {size:,} ({size/sum(sizes)*100:.1f}%)"
            for label, size in zip(labels, sizes)
        ]
        ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path
    
    def create_category_bar_chart(
        self,
        category_data: dict,
        filename: str = "category_comparison.png"
    ):
        """
        Create grouped bar chart comparing categories
        """
        print(f"\n📊 Creating category comparison chart...")
        
        categories = category_data['categories']
        
        # Prepare data
        df = pd.DataFrame(categories)
        df['category'] = df['category'].str.replace('_', ' ').str.title()
        df = df.sort_values('total_demand', ascending=False).head(10)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Chart 1: Total demand
        bars1 = ax1.bar(range(len(df)), df['total_demand'], color=sns.color_palette(COLOR_PALETTE, len(df)))
        ax1.set_xticks(range(len(df)))
        ax1.set_xticklabels(df['category'], rotation=45, ha='right')
        ax1.set_ylabel('Total Demand', fontsize=11, fontweight='bold')
        ax1.set_title('Total Skill Demand by Category', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(df['total_demand']):
            ax1.text(i, v + max(df['total_demand']) * 0.01, f"{v:,}", ha='center', va='bottom', fontsize=9)
        
        # Chart 2: Unique skills
        bars2 = ax2.bar(range(len(df)), df['unique_skills'], color=sns.color_palette(COLOR_PALETTE, len(df)))
        ax2.set_xticks(range(len(df)))
        ax2.set_xticklabels(df['category'], rotation=45, ha='right')
        ax2.set_ylabel('Unique Skills', fontsize=11, fontweight='bold')
        ax2.set_title('Unique Skills by Category', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(df['unique_skills']):
            ax2.text(i, v + max(df['unique_skills']) * 0.01, f"{v}", ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path
    
    def create_cooccurrence_heatmap(
        self,
        cooccurrence_data: dict,
        top_n: int = 20,
        filename: str = "skill_cooccurrence_heatmap.png"
    ):
        """
        Create heatmap of skill co-occurrence
        """
        print(f"\n🔥 Creating co-occurrence heatmap...")
        
        pairs = cooccurrence_data['pairs'][:50]  # Top 50 pairs
        
        if not pairs:
            print("   ⚠️  No co-occurrence data available")
            return None
        
        # Get top N skills from pairs
        skills = set()
        for pair in pairs:
            skills.add(pair['skill_1'])
            skills.add(pair['skill_2'])
            if len(skills) >= top_n:
                break
        
        skills = sorted(list(skills))[:top_n]
        
        # Create matrix
        matrix = np.zeros((len(skills), len(skills)))
        
        for pair in pairs:
            if pair['skill_1'] in skills and pair['skill_2'] in skills:
                i = skills.index(pair['skill_1'])
                j = skills.index(pair['skill_2'])
                matrix[i][j] = pair['cooccurrence_count']
                matrix[j][i] = pair['cooccurrence_count']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Create heatmap
        sns.heatmap(
            matrix,
            xticklabels=skills,
            yticklabels=skills,
            annot=True,
            fmt='.0f',
            cmap='YlOrRd',
            cbar_kws={'label': 'Co-occurrence Count'},
            ax=ax,
            square=True
        )
        
        ax.set_title(f'Top {top_n} Skills Co-occurrence Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path
    
    def create_top_pairs_chart(
        self,
        cooccurrence_data: dict,
        top_n: int = 15,
        filename: str = "top_skill_pairs.png"
    ):
        """
        Create bar chart of top skill pairs
        """
        print(f"\n📊 Creating top skill pairs chart...")
        
        pairs = cooccurrence_data['pairs'][:top_n]
        
        if not pairs:
            print("   ⚠️  No co-occurrence data available")
            return None
        
        # Prepare data
        labels = [f"{p['skill_1']} + {p['skill_2']}" for p in pairs]
        counts = [p['cooccurrence_count'] for p in pairs]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.4)))
        
        # Create horizontal bar chart
        bars = ax.barh(
            range(len(pairs)),
            counts,
            color=sns.color_palette(COLOR_PALETTE, len(pairs))
        )
        
        # Customize
        ax.set_yticks(range(len(pairs)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel('Co-occurrence Count', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Skill Pairs (Frequently Appear Together)', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels
        for i, count in enumerate(counts):
            ax.text(count + max(counts) * 0.01, i, f"{count:,}", va='center', fontsize=9)
        
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path
    
    def create_summary_dashboard(
        self,
        summary: dict,
        frequency_data: pd.DataFrame,
        category_data: dict,
        filename: str = "summary_dashboard.png"
    ):
        """
        Create summary dashboard with key metrics
        """
        print(f"\n📈 Creating summary dashboard...")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Color palette
        colors = sns.color_palette(COLOR_PALETTE, 10)
        
        # 1. Key Metrics (top left)
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        metrics_text = f"""
        📊 SKILLS DEMAND ANALYSIS SUMMARY
        
        Total Jobs Analyzed: {summary['total_jobs_analyzed']:,}
        Total Unique Skills: {summary['total_unique_skills']:,}
        Total Categories: {summary['total_categories']}
        Average Skills per Job: {summary['avg_skills_per_job']}
        
        Top 3 Most Demanded Skills:
        1. {summary['top_3_skills'][0] if len(summary['top_3_skills']) > 0 else 'N/A'}
        2. {summary['top_3_skills'][1] if len(summary['top_3_skills']) > 1 else 'N/A'}
        3. {summary['top_3_skills'][2] if len(summary['top_3_skills']) > 2 else 'N/A'}
        """
        
        ax1.text(0.5, 0.5, metrics_text, ha='center', va='center', fontsize=11, 
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        # 2. Top 10 Skills (middle left)
        ax2 = fig.add_subplot(gs[1:, 0])
        top10 = frequency_data.head(10)
        ax2.barh(range(len(top10)), top10['demand_count'], color=colors[:len(top10)])
        ax2.set_yticks(range(len(top10)))
        ax2.set_yticklabels(top10['skill'])
        ax2.invert_yaxis()
        ax2.set_xlabel('Demand Count')
        ax2.set_title('Top 10 Skills', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. Category Distribution (middle center)
        ax3 = fig.add_subplot(gs[1, 1:])
        categories = category_data['categories'][:8]
        cat_labels = [c['category'].replace('_', ' ').title() for c in categories]
        cat_sizes = [c['total_demand'] for c in categories]
        ax3.pie(cat_sizes, labels=cat_labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax3.set_title('Category Distribution', fontweight='bold')
        
        # 4. Skills per Category (bottom right)
        ax4 = fig.add_subplot(gs[2, 1:])
        cat_skills = [c['unique_skills'] for c in categories]
        ax4.bar(range(len(categories)), cat_skills, color=colors[:len(categories)])
        ax4.set_xticks(range(len(categories)))
        ax4.set_xticklabels([c[:10] for c in cat_labels], rotation=45, ha='right')
        ax4.set_ylabel('Unique Skills')
        ax4.set_title('Unique Skills by Category', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        plt.suptitle('Skills Demand Analysis Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return output_path


def generate_all_visualizations(limit: int = None):
    """Generate all visualizations from database analysis"""
    
    print("\n" + "=" * 70)
    print("GENERATE VISUALIZATIONS - MODULE #4")
    print("=" * 70)
    
    # Get database connection
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
    )
    
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Run analysis
        print(f"\n🔍 Running skills demand analysis...")
        if limit:
            print(f"   Analyzing {limit:,} jobs (sample)")
        else:
            print(f"   Analyzing ALL jobs")
        
        service = SkillDemandService(db)
        results = service.run_complete_analysis(limit=limit, top_n=50, min_cooccurrence=5)
        
        if 'error' in results:
            print(f"\n❌ Error: {results['error']}")
            return
        
        print(f"   ✅ Analyzed {results['summary']['total_jobs_analyzed']:,} jobs")
        print(f"   ✅ Found {results['summary']['total_unique_skills']:,} unique skills")
        
        # Convert to DataFrame
        frequency_df = pd.DataFrame(results['frequency']['skills'])
        
        # Initialize generator
        generator = VisualizationGenerator()
        
        # Generate visualizations
        print(f"\n🎨 Generating visualizations...")
        
        viz_files = []
        
        # 1. Top skills bar chart
        viz_files.append(generator.create_top_skills_bar_chart(frequency_df, top_n=30))
        
        # 2. Category pie chart
        viz_files.append(generator.create_category_pie_chart(results['category_distribution']))
        
        # 3. Category comparison
        viz_files.append(generator.create_category_bar_chart(results['category_distribution']))
        
        # 4. Co-occurrence heatmap
        heatmap = generator.create_cooccurrence_heatmap(results['cooccurrence'], top_n=20)
        if heatmap:
            viz_files.append(heatmap)
        
        # 5. Top pairs chart
        pairs = generator.create_top_pairs_chart(results['cooccurrence'], top_n=15)
        if pairs:
            viz_files.append(pairs)
        
        # 6. Summary dashboard
        viz_files.append(generator.create_summary_dashboard(
            results['summary'],
            frequency_df,
            results['category_distribution']
        ))
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ VISUALIZATION GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nGenerated {len([v for v in viz_files if v])} visualizations:")
        for viz_file in viz_files:
            if viz_file:
                print(f"   📊 {viz_file.name}")
        
        print(f"\n📁 Output directory: {generator.output_dir.absolute()}")
        print("\n💡 Next steps:")
        print("   1. Review visualizations")
        print("   2. Include in reports/presentations")
        print("   3. Upload to portfolio")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate skills demand visualizations")
    parser.add_argument('--limit', type=int, default=None, help='Limit number of jobs to analyze')
    
    args = parser.parse_args()
    
    generate_all_visualizations(limit=args.limit)