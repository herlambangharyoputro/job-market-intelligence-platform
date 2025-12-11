# Annotation System - Complete Documentation

## 🎯 Project Overview

**Job Market Intelligence Platform** dengan sistem annotation komprehensif untuk analisis lowongan pekerjaan menggunakan NLP dan Machine Learning.

### Goals
- Menganalisis data lowongan pekerjaan dari scraping
- Melakukan annotation otomatis dan manual
- Mengekstrak insights dari job market
- Menyediakan API untuk frontend dan analytics

## 📊 Database Architecture

### Entity Relationship Diagram (Conceptual)

```
jobs (1) ----< (*) annotations
               |
               |---< (*) annotation_history
               |
               +---- (1) annotation_types
               +---- (1) annotators
               
annotation_types (1) ----< (*) annotation_labels
                    +----< (*) annotation_rules

annotators (1) ----< (*) annotation_tasks

annotations (1) ----< (1) annotation_quality
```

### Table Categories

#### 1. Core Annotation System
- `jobs` - Source data
- `annotations` - Main annotations
- `annotation_types` - Type definitions
- `annotation_labels` - Label catalog
- `annotation_rules` - Auto-annotation logic
- `annotation_history` - Audit trail
- `annotators` - Users/systems
- `annotation_tasks` - Task management
- `annotation_quality` - Quality metrics

#### 2. Supporting Taxonomies
- `skills_taxonomy` - Hierarchical skills
- `location_mappings` - Location normalization
- `company_profiles` - Company data
- `salary_ranges` - Salary benchmarks
- `job_categories` - Job classification
- `benefit_categories` - Benefits catalog

## 🚀 Setup Instructions

### Prerequisites

```bash
# 1. Python 3.10+
python --version

# 2. MySQL 8.0+
mysql --version

# 3. Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd job-market-intelligence-platform/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 4. Run migrations
python run_migrations.py

# 5. Seed initial data
python seed_initial_data.py
```

## 📁 Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files (001-015)
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── README.md               # Migration docs
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # API routes
│   │           ├── jobs.py
│   │           ├── annotations.py
│   │           ├── annotation_types.py
│   │           ├── tokenization.py
│   │           └── analytics.py
│   ├── models/                 # SQLAlchemy models
│   │   ├── job.py
│   │   ├── annotation.py
│   │   ├── annotation_type.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── job.py
│   │   ├── annotation.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── preprocessing/
│   │   │   └── tokenizers/     # Per-entity tokenizers
│   │   ├── nlp/
│   │   │   ├── ner.py
│   │   │   ├── skill_extraction.py
│   │   │   └── sentiment.py
│   │   └── annotation/
│   │       ├── auto_annotator.py
│   │       ├── quality_checker.py
│   │       └── task_manager.py
│   ├── database/
│   │   ├── base.py
│   │   └── session.py
│   └── core/
│       ├── config.py
│       └── dependencies.py
├── data/
│   └── raw/
│       └── lokerid/            # XLSX files
├── scripts/
│   ├── migrate_xlsx_to_mysql.py
│   ├── seed_initial_data.py
│   └── batch_tokenize.py
├── alembic.ini
├── run_migrations.py
└── requirements.txt
```

## 🔄 Data Flow

### 1. Data Ingestion (XLSX → MySQL)

```python
# scripts/migrate_xlsx_to_mysql.py
XLSX Files → Pandas DataFrame → Transform → MySQL (jobs table)
```

**Process:**
- Read XLSX from `data/raw/lokerid/`
- Parse dates, extract salary ranges
- Normalize text fields
- Deduplicate by URL
- Batch insert to `jobs` table

### 2. Tokenization Pipeline

```python
# Per entity tokenizer
Job Text → Tokenizer → Tokens → Database
```

**Tokenizers:**
- `JobTitleTokenizer` - Process job titles
- `DescriptionTokenizer` - Process descriptions
- `SkillTokenizer` - Extract skills
- `LocationTokenizer` - Parse locations

### 3. Auto-Annotation Pipeline

```
Jobs → Rules Engine → Annotations
     → NLP Models  → Annotations
     → Dictionary  → Annotations
```

**Types:**
- **NER**: Extract entities (companies, locations, technologies)
- **Skill Extraction**: Identify technical and soft skills
- **Sentiment Analysis**: Analyze job description tone
- **Category Classification**: Auto-categorize jobs

### 4. Manual Annotation

```
Annotator → Task → Jobs → Annotations → Validation
```

**Workflow:**
1. Admin creates annotation task
2. Assigns to annotator
3. Annotator labels jobs
4. Validator reviews
5. Accepted/Rejected

## 📝 API Endpoints

### Jobs

```
GET    /api/v1/jobs                    # List jobs
GET    /api/v1/jobs/{id}               # Get job detail
POST   /api/v1/jobs                    # Create job
PUT    /api/v1/jobs/{id}               # Update job
DELETE /api/v1/jobs/{id}               # Delete job
GET    /api/v1/jobs/unannotated        # Get unannotated jobs
```

### Annotations

```
POST   /api/v1/annotations             # Create annotation
GET    /api/v1/annotations/{job_id}    # Get annotations for job
PUT    /api/v1/annotations/{id}        # Update annotation
DELETE /api/v1/annotations/{id}        # Delete annotation
POST   /api/v1/annotations/batch       # Batch create
POST   /api/v1/annotations/validate    # Validate annotation
```

### Annotation Types

```
GET    /api/v1/annotation-types        # List types
POST   /api/v1/annotation-types        # Create type
GET    /api/v1/annotation-types/{id}/labels  # Get labels for type
```

### Tokenization

```
POST   /api/v1/tokenize/job-title      # Tokenize title
POST   /api/v1/tokenize/description    # Tokenize description
POST   /api/v1/tokenize/skills         # Tokenize skills
POST   /api/v1/tokenize/batch          # Batch tokenize
```

### Analytics

```
GET    /api/v1/analytics/annotations/stats      # Annotation statistics
GET    /api/v1/analytics/quality/metrics        # Quality metrics
GET    /api/v1/analytics/skills/demand          # Skill demand
GET    /api/v1/analytics/salary/trends          # Salary trends
```

## 🎨 Annotation Types

### 1. Named Entity Recognition (NER)

**Entities:**
- `COMPANY` - Company names
- `LOCATION` - Locations (cities, provinces)
- `TECHNOLOGY` - Technologies (Python, React, etc)
- `TOOL` - Tools (Git, Docker, etc)
- `CERTIFICATION` - Certifications (AWS, PMP, etc)

### 2. Skill Extraction

**Categories:**
- `SKILL_TECH` - Technical skills
- `SKILL_SOFT` - Soft skills
- `SKILL_LANGUAGE` - Language skills
- `SKILL_TOOL` - Tools and software

### 3. Sentiment Analysis

**Sentiments:**
- `POSITIVE` - Positive tone
- `NEUTRAL` - Neutral tone
- `NEGATIVE` - Negative tone

**Aspects:**
- Company description
- Job requirements
- Work environment

### 4. Job Classification

**Categories:**
- `CATEGORY_IT` - IT/Technology
- `CATEGORY_FINANCE` - Finance
- `CATEGORY_MARKETING` - Marketing
- etc.

### 5. Requirement Extraction

**Types:**
- `REQ_EDUCATION` - Education requirements
- `REQ_EXPERIENCE` - Experience requirements
- `REQ_CERTIFICATION` - Certification requirements

### 6. Benefit Extraction

**Categories:**
- `BENEFIT_HEALTH` - Health benefits
- `BENEFIT_WORKLIFE` - Work-life balance
- `BENEFIT_FINANCIAL` - Financial benefits
- `BENEFIT_DEVELOPMENT` - Career development

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=mysql+pymysql://root@localhost:3306/job_market_intelligence_platform

# API Settings
API_V1_PREFIX=/api/v1
DEBUG=True

# NLP Settings
MAX_TEXT_LENGTH=10000
DEFAULT_LANGUAGE=id
ENABLE_SENTIMENT_ANALYSIS=True
ENABLE_SKILL_EXTRACTION=True

# Annotation Settings
AUTO_ANNOTATION_ENABLED=True
MIN_CONFIDENCE_THRESHOLD=0.7
BATCH_SIZE=100
```

## 📊 Monitoring & Quality

### Quality Metrics

1. **Accuracy Score** (0-1)
   - How accurate is the annotation
   - Compared to gold standard

2. **Consistency Score** (0-1)
   - Consistency with other annotators
   - Inter-annotator agreement

3. **Completeness Score** (0-1)
   - How complete is the annotation
   - All required fields annotated

4. **Kappa Score** (0-1)
   - Cohen's Kappa for agreement
   - Statistical measure

### Performance Tracking

```sql
-- Annotator performance
SELECT 
    a.username,
    COUNT(*) as total_annotations,
    AVG(aq.overall_quality) as avg_quality,
    a.agreement_score
FROM annotators a
LEFT JOIN annotations an ON an.annotator_id = a.id
LEFT JOIN annotation_quality aq ON aq.annotation_id = an.id
GROUP BY a.id;
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tokenizers.py

# Run with coverage
pytest --cov=app tests/
```

### Integration Tests

```bash
# Test API endpoints
pytest tests/integration/test_api.py

# Test annotation pipeline
pytest tests/integration/test_annotation_pipeline.py
```

## 📈 Performance Optimization

### Database

1. **Indexes**: Strategic indexes on foreign keys and query patterns
2. **Partitioning**: Partition large tables by date
3. **Caching**: Redis for frequently accessed data

### API

1. **Pagination**: Limit result sets
2. **Async**: Use async/await for I/O operations
3. **Batch Processing**: Process multiple items together

### NLP

1. **Model Loading**: Load models once, keep in memory
2. **Batch Inference**: Process multiple texts together
3. **GPU**: Use GPU for heavy models

## 🔐 Security

### Authentication

- JWT tokens for API access
- Role-based access control (RBAC)
- API rate limiting

### Data Privacy

- No PII in annotations
- Audit trail for all changes
- Data encryption at rest

## 📚 Resources

### Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [spaCy Docs](https://spacy.io/)

### Tools

- [DB Browser for SQLite](https://sqlitebrowser.org/) - For viewing SQLite
- [MySQL Workbench](https://www.mysql.com/products/workbench/) - For MySQL
- [Postman](https://www.postman.com/) - For API testing

## 🐛 Troubleshooting

### Common Issues

**1. Migration fails**
```bash
# Check current version
alembic current

# Stamp to specific version
alembic stamp 001

# Re-run
alembic upgrade head
```

**2. Import errors**
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**3. Database connection fails**
```bash
# Test connection
python -c "from app.database import engine; engine.connect()"

# Check MySQL
mysql -u root -p -e "SHOW DATABASES;"
```

## 🎯 Roadmap

### Phase 1: Setup ✅
- [x] Database schema design
- [x] Alembic migrations
- [x] Initial documentation

### Phase 2: Data Migration (Next)
- [ ] XLSX to MySQL migration script
- [ ] Data validation
- [ ] Initial data analysis

### Phase 3: Tokenization
- [ ] Implement tokenizers
- [ ] Batch processing
- [ ] Performance optimization

### Phase 4: Auto-Annotation
- [ ] NER pipeline
- [ ] Skill extraction
- [ ] Sentiment analysis
- [ ] Rule engine

### Phase 5: Manual Annotation
- [ ] Task management
- [ ] Annotation interface
- [ ] Validation workflow

### Phase 6: Quality & Testing
- [ ] Quality metrics
- [ ] Inter-annotator agreement
- [ ] Unit & integration tests

## 📞 Contact

For questions or issues:
- Check documentation
- Review migration logs
- Check database status

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-11  
**Database Schema Version**: 015 (15 tables)
