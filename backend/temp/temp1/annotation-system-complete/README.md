# 🚀 Annotation System - Complete Package

## 📦 Package Contents

Sistem annotation lengkap untuk **Job Market Intelligence Platform** dengan 15 tabel database yang telah dioptimasi.

### 📂 Struktur File

```
annotation-system-complete/
├── README.md                          ← Anda di sini
├── DELIVERY_SUMMARY.md                ← Ringkasan lengkap deliverables
├── DOCUMENTATION.md                   ← Dokumentasi teknis lengkap
│
├── alembic.ini                        ← Konfigurasi Alembic
├── run_migrations.py                  ← Script untuk run migrations
├── seed_initial_data.py               ← Script untuk seed data awal
│
└── alembic/
    ├── README.md                      ← Panduan migrations
    ├── env.py                         ← Environment Alembic
    ├── script.py.mako                 ← Template migration
    └── versions/                      ← 15 migration files
        ├── 001_create_jobs_table.py
        ├── 002_create_annotation_types.py
        ├── 003_create_annotations.py
        ├── 004_create_annotation_labels.py
        ├── 005_create_annotation_rules.py
        ├── 006_create_annotation_history.py
        ├── 007_create_annotators.py
        ├── 008_create_annotation_tasks.py
        ├── 009_create_annotation_quality.py
        ├── 010_create_skills_taxonomy.py
        ├── 011_create_location_mappings.py
        ├── 012_create_company_profiles.py
        ├── 013_create_salary_ranges.py
        ├── 014_create_job_categories.py
        └── 015_create_benefit_categories.py
```

---

## 🎯 Quick Start (3 Steps)

### Step 1: Copy Files to Your Project

```bash
# Copy semua file ke backend project Anda
cp -r annotation-system-complete/* /path/to/job-market-intelligence-platform/backend/

# Atau copy manual:
# - Folder alembic/ → backend/alembic/
# - File alembic.ini → backend/alembic.ini
# - File run_migrations.py → backend/run_migrations.py
# - File seed_initial_data.py → backend/seed_initial_data.py
```

### Step 2: Run Migrations

```bash
cd /path/to/job-market-intelligence-platform/backend

# Method 1: Gunakan script Python (Recommended)
python run_migrations.py

# Method 2: Gunakan Alembic langsung
alembic upgrade head
```

### Step 3: Seed Initial Data

```bash
python seed_initial_data.py
```

**Done!** 15 tabel sudah dibuat di MySQL Anda ✅

---

## 📊 Database Schema

### 15 Tables Created

#### **Core Annotation System** (9 tables)
1. **jobs** - Data lowongan dari scraping (20 columns)
2. **annotation_types** - Jenis-jenis annotation (NER, Skill, Sentiment, dll)
3. **annotations** - Data annotation utama dengan confidence scoring
4. **annotation_labels** - Master labels untuk setiap type
5. **annotation_rules** - Rules untuk auto-annotation
6. **annotation_history** - Audit trail semua perubahan
7. **annotators** - User/system yang melakukan annotation
8. **annotation_tasks** - Task management dan assignment
9. **annotation_quality** - Quality metrics dan validation

#### **Supporting Taxonomies** (6 tables)
10. **skills_taxonomy** - Hierarchical skill organization
11. **location_mappings** - Location normalization (raw → normalized)
12. **company_profiles** - Company information dan statistics
13. **salary_ranges** - Salary benchmarks per position/location
14. **job_categories** - Job categorization hierarchy
15. **benefit_categories** - Benefits taxonomy

---

## 📖 Documentation Files

### 1. DELIVERY_SUMMARY.md
**Apa isinya:**
- Checklist lengkap deliverables
- Quick start guide
- Verification checklist
- Troubleshooting tips
- Success criteria

**Kapan baca:**
- Saat ingin overview lengkap
- Sebelum mulai implementasi
- Untuk verifikasi semua file ada

### 2. DOCUMENTATION.md
**Apa isinya:**
- Architecture diagram
- Setup instructions lengkap
- API endpoints design
- Annotation types explained
- Configuration options
- Testing strategies

**Kapan baca:**
- Saat develop fitur baru
- Butuh referensi teknis
- Planning implementasi

### 3. alembic/README.md
**Apa isinya:**
- Migration commands
- Table descriptions
- Common operations
- SQL queries examples
- Troubleshooting migrations

**Kapan baca:**
- Masalah dengan migrations
- Butuh rollback
- Mau lihat struktur tabel detail

---

## ⚡ Common Commands

### Migrations

```bash
# Check status
alembic current

# View history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade 010

# Downgrade one step
alembic downgrade -1

# Rollback all
alembic downgrade base
```

### MySQL Verification

```bash
# Login to MySQL
mysql -u root -p job_market_intelligence_platform

# Check tables
mysql> SHOW TABLES;

# Count rows
mysql> SELECT COUNT(*) FROM jobs;
mysql> SELECT COUNT(*) FROM annotation_types;

# View structure
mysql> DESCRIBE jobs;
mysql> DESCRIBE annotations;
```

---

## 🔍 What Each Migration Does

| Migration | Table | Purpose | Key Features |
|-----------|-------|---------|--------------|
| 001 | jobs | Store job postings | 20 columns, salary parsing, processing flags |
| 002 | annotation_types | Define annotation types | Category grouping, validation flags |
| 003 | annotations | Core annotations | Offset-based, confidence scoring, status |
| 004 | annotation_labels | Label catalog | Hierarchical, synonyms, usage tracking |
| 005 | annotation_rules | Auto-annotation rules | Regex, ML models, dictionary support |
| 006 | annotation_history | Audit trail | Complete change tracking |
| 007 | annotators | Users/systems | Human/AI types, permissions, stats |
| 008 | annotation_tasks | Task management | Assignment, progress, deadlines |
| 009 | annotation_quality | Quality metrics | Accuracy, consistency, Kappa scores |
| 010 | skills_taxonomy | Skills hierarchy | Hard/soft skills, demand tracking |
| 011 | location_mappings | Location normalize | Geographic coordinates, hierarchy |
| 012 | company_profiles | Company data | Industry, size, hiring stats |
| 013 | salary_ranges | Salary benchmarks | Statistical measures, trends |
| 014 | job_categories | Job classification | Auto-classification, market insights |
| 015 | benefit_categories | Benefits taxonomy | Monetary/non-monetary, impact |

---

## 🎯 Next Steps After Setup

### Phase 2: Data Migration
1. Create XLSX migration script
2. Import November 2025 data
3. Import December 2025 data
4. Validate data integrity

**Script location:** `scripts/migrate_xlsx_to_mysql.py` (to be created)

### Phase 3: Tokenization
1. Implement tokenizers per entity
2. Setup batch processing
3. Test tokenization quality

**Script location:** `scripts/batch_tokenize.py` (to be created)

### Phase 4: Auto-Annotation
1. Implement NER pipeline
2. Build skill extraction
3. Create sentiment analyzer
4. Develop classifiers

**Service location:** `app/services/nlp/` (to be implemented)

---

## 💡 Tips & Best Practices

### 1. Before Running Migrations

✅ **DO:**
- Backup database jika ada
- Verify DATABASE_URL di .env
- Check MySQL is running
- Review migration files first

❌ **DON'T:**
- Run di production tanpa testing
- Edit migration files after running
- Skip verification steps

### 2. Naming Conventions

**Tables:** Lowercase, underscore-separated (e.g., `annotation_types`)  
**Columns:** Lowercase, underscore-separated (e.g., `created_at`)  
**Foreign Keys:** `{table}_id` (e.g., `job_id`, `annotation_type_id`)  
**Indexes:** `idx_{table}_{columns}` (e.g., `idx_jobs_company_location`)

### 3. Database Performance

- **Use indexes** untuk columns yang sering di-query
- **JSON columns** untuk flexible data (metadata, lists)
- **Enum types** untuk fixed values (status, types)
- **Timestamps** auto-update dengan MySQL triggers

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Pastikan di directory backend
cd backend

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add __init__.py files
touch app/__init__.py
```

### Issue: "Can't locate revision identified by '001'"

**Solution:**
```bash
# Reset Alembic version
alembic stamp base

# Re-run migrations
alembic upgrade head
```

### Issue: "Table already exists"

**Solution:**
```bash
# Option 1: Drop table manually
mysql> DROP TABLE jobs;

# Option 2: Stamp to skip migration
alembic stamp 001
```

---

## ✅ Verification Checklist

Setelah run migrations, pastikan:

- [ ] Command `alembic current` menunjukkan version `015`
- [ ] MySQL memiliki 16 tables (15 + alembic_version)
- [ ] Table `jobs` memiliki 20+ columns
- [ ] Table `annotations` memiliki foreign keys working
- [ ] Seed script berhasil insert data
- [ ] Query test berjalan tanpa error

---

## 📞 Support

Jika ada pertanyaan atau issues:

1. **Check Documentation**: Baca DOCUMENTATION.md untuk detail teknis
2. **Review Migrations**: Lihat migration files untuk struktur tabel
3. **Check Logs**: Review error messages di console
4. **Verify Setup**: Run verification commands

---

## 📄 License & Credits

**Project**: Job Market Intelligence Platform  
**Module**: Annotation System  
**Version**: 1.0.0  
**Date**: 2025-12-11  

**Technologies Used:**
- FastAPI (Web framework)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- MySQL (Database)
- Python 3.10+

---

## 🎉 Ready to Go!

Semua file sudah siap untuk digunakan. Follow Quick Start guide di atas dan Anda siap untuk Phase 2!

**Happy Coding! 🚀**
