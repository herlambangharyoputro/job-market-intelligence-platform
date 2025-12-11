# Database Migration Guide - Annotation System

## 📋 Overview

Sistem migration database untuk **Job Market Intelligence Platform** menggunakan Alembic. Total 15 tabel telah dirancang untuk mendukung sistem annotation yang komprehensif.

## 🗄️ Database Schema

### Core Tables (Jobs & Annotations)

1. **jobs** - Data lowongan pekerjaan dari scraping
   - 20 kolom dari data XLSX
   - Support untuk salary parsing, processing flags
   - Indexes untuk query performa

2. **annotation_types** - Master jenis annotation
   - NER, Sentiment, Skill Extraction, dll
   - Konfigurasi per-type (multiple allowed, validation required)

3. **annotations** - Data annotation utama
   - Support offset-based annotation
   - Confidence scoring untuk auto-annotation
   - Status tracking (pending, validated, rejected)

4. **annotation_labels** - Master labels untuk setiap type
   - Hierarchical structure
   - Synonyms dan examples
   - Usage tracking

5. **annotation_rules** - Rules untuk auto-annotation
   - Support regex, keyword, ML model, dictionary
   - Priority dan execution order
   - Performance metrics

6. **annotation_history** - Audit trail
   - Track semua perubahan annotation
   - Who, what, when tracking

7. **annotators** - User/System annotators
   - Human, AI, Rule engine, Hybrid
   - Permission management
   - Performance metrics (agreement score)

8. **annotation_tasks** - Task management
   - Assignment dan deadline tracking
   - Progress monitoring
   - Filter-based job selection

9. **annotation_quality** - Quality metrics
   - Accuracy, consistency, completeness scores
   - Inter-annotator agreement (Kappa score)
   - Gold standard marking

### Supporting Tables

10. **skills_taxonomy** - Hierarchical skill organization
    - Hard vs Soft skills
    - Market demand tracking
    - Related skills mapping

11. **location_mappings** - Location normalization
    - Raw → Normalized mapping
    - Geographic coordinates
    - Hierarchy (Country → Province → City)

12. **company_profiles** - Company information
    - Industry, size, culture
    - Hiring statistics
    - Social media links

13. **salary_ranges** - Salary benchmarks
    - Per position, level, location
    - Statistical measures (avg, median, percentiles)
    - Trending data

14. **job_categories** - Job categorization
    - Hierarchical structure
    - Auto-classification rules
    - Market insights

15. **benefit_categories** - Benefit taxonomy
    - Monetary vs non-monetary
    - Prevalence and popularity
    - Impact on retention

## 🚀 Quick Start

### Prerequisites

```bash
# Pastikan MySQL sudah berjalan
# Database: job_market_intelligence_platform

# Install dependencies (jika belum)
pip install alembic sqlalchemy pymysql
```

### Configuration

File `alembic.ini` sudah dikonfigurasi dengan:
```ini
sqlalchemy.url = mysql+pymysql://root@localhost:3306/job_market_intelligence_platform
```

Sesuaikan dengan credentials MySQL Anda jika berbeda.

### Initialize Alembic (Already Done)

```bash
# Struktur sudah dibuat, skip step ini
# alembic init alembic
```

### Run Migrations

```bash
# Method 1: Run all migrations
alembic upgrade head

# Method 2: Run migrations one by one
alembic upgrade 001  # Jobs table
alembic upgrade 002  # Annotation types
alembic upgrade 003  # Annotations
# ... dst

# Method 3: Run specific migration
alembic upgrade 001:005  # Run migration 001 through 005
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

### Downgrade (Rollback)

```bash
# Rollback to specific version
alembic downgrade 014

# Rollback one step
alembic downgrade -1

# Rollback all
alembic downgrade base
```

## 📊 Migration Files

| File | Table | Description |
|------|-------|-------------|
| 001 | jobs | Main job postings data |
| 002 | annotation_types | Annotation type definitions |
| 003 | annotations | Core annotations data |
| 004 | annotation_labels | Label definitions |
| 005 | annotation_rules | Auto-annotation rules |
| 006 | annotation_history | Change tracking |
| 007 | annotators | User/system annotators |
| 008 | annotation_tasks | Task management |
| 009 | annotation_quality | Quality metrics |
| 010 | skills_taxonomy | Skills hierarchy |
| 011 | location_mappings | Location normalization |
| 012 | company_profiles | Company data |
| 013 | salary_ranges | Salary benchmarks |
| 014 | job_categories | Job categorization |
| 015 | benefit_categories | Benefits taxonomy |

## 🔍 Key Features

### Multi-level Hierarchies
- Skills taxonomy (root → category → skill)
- Job categories (industry → function → specialty)
- Benefits (category → subcategory → benefit)
- Locations (country → province → city)

### Annotation System
- **Multiple annotation methods**: Manual, Auto, Semi-auto
- **Confidence scoring**: 0-1 untuk auto-annotations
- **Status tracking**: Pending → In Review → Validated/Rejected
- **Quality metrics**: Accuracy, consistency, completeness
- **Inter-annotator agreement**: Kappa scores

### Performance Optimization
- **Strategic indexes** pada semua foreign keys
- **Composite indexes** untuk common query patterns
- **JSON columns** untuk flexible data
- **Materialized paths** untuk hierarchy queries

## 🛠️ Common Operations

### Add New Annotation Type

```sql
INSERT INTO annotation_types (code, name, category, entity_field)
VALUES ('SKILL_TECH', 'Technical Skills', 'Extraction', 'keahlian');
```

### Create Auto-annotation Rule

```sql
INSERT INTO annotation_rules (
    annotation_type_id, 
    rule_name, 
    rule_type, 
    pattern,
    min_confidence
) VALUES (
    1, 
    'Extract Python Skills', 
    'regex', 
    'python|django|flask',
    0.8
);
```

### Query Jobs Needing Annotation

```sql
SELECT * FROM jobs 
WHERE is_processed = TRUE 
  AND is_annotated = FALSE
LIMIT 100;
```

### Get Annotation Statistics

```sql
SELECT 
    at.name,
    COUNT(*) as total_annotations,
    AVG(a.confidence_score) as avg_confidence
FROM annotations a
JOIN annotation_types at ON a.annotation_type_id = at.id
GROUP BY at.name;
```

## 📝 Next Steps

Setelah migrations berhasil:

1. **Seed Initial Data**
   - Annotation types (NER, Skill, Sentiment, dll)
   - Basic skills taxonomy
   - Location mappings
   - Benefit categories

2. **Data Migration dari XLSX**
   - Import November 2025 data
   - Import December 2025 data
   - Validate data integrity

3. **Setup Tokenization**
   - Create tokenizer per entity
   - Configure batch processing

4. **Implement Auto-annotation**
   - NER pipeline
   - Skill extraction
   - Sentiment analysis

## ⚠️ Important Notes

### MySQL-specific Features

Migrations menggunakan MySQL-specific features:
- `ON UPDATE CURRENT_TIMESTAMP` untuk auto-update timestamps
- `mysql_engine='InnoDB'` untuk transaction support
- `mysql_charset='utf8mb4'` untuk emoji/unicode support

### Foreign Key Constraints

- **CASCADE** pada annotation_history → annotations (hapus history jika annotation dihapus)
- **RESTRICT** pada annotations → annotation_types (prevent deleting types yang masih digunakan)
- **SET NULL** pada optional relationships

### Enum Types

Beberapa tabel menggunakan ENUM untuk data integrity:
- annotation_method: manual, auto, semi_auto
- annotation_status: pending, validated, rejected, in_review
- task_priority: low, medium, high, urgent
- skill_type: hard, soft, technical, language, certification

## 🐛 Troubleshooting

### Migration Fails

```bash
# Check connection
mysql -u root -p -e "SHOW DATABASES;"

# Check current version
alembic current

# Show pending migrations
alembic show head

# Force stamp to specific version (use with caution!)
alembic stamp 001
```

### Reset Everything

```bash
# Drop all tables
alembic downgrade base

# Re-run all migrations
alembic upgrade head
```

### Check Table Creation

```sql
-- In MySQL
USE job_market_intelligence_platform;
SHOW TABLES;
DESCRIBE jobs;
DESCRIBE annotations;
```

## 📚 References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 📧 Support

Jika ada pertanyaan atau issues, silakan check:
1. Migration logs di console
2. MySQL error logs
3. Alembic version history

---

**Generated**: 2025-12-11
**Version**: 1.0.0
**Database**: MySQL 8.0+
**Total Tables**: 15
