-- ============================================================================
-- Phase 4: Tokenization Storage - Level 2 & 3 (Detailed + Embeddings)
-- Purpose: ML training, NLP processing, semantic search
-- Implement: When starting ML modules (Phase 6-10)
-- ============================================================================

USE job_market_intelligence_platform;

-- ============================================================================
-- LEVEL 2: Detailed Tokenization Table
-- Purpose: Full tokenization data for ML models
-- Size: ~3 KB per job
-- Used by: HF Datasets #3, #4, #7, Models #1-8
-- ============================================================================

CREATE TABLE IF NOT EXISTS job_tokens_detailed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL UNIQUE,
    
    -- Title Tokens (Full)
    title_tokens JSON COMMENT 'All title tokens with positions',
    title_level VARCHAR(50),
    title_role VARCHAR(100),
    title_tech_stack JSON,
    title_location VARCHAR(100),
    title_confidence DECIMAL(3,2),
    title_normalized VARCHAR(255),
    
    -- Skills Tokens (CRITICAL for Models #1, #4, #5)
    skills_all JSON COMMENT 'All skills with metadata',
    skills_categorized JSON COMMENT 'Skills grouped by category',
    skills_proficiency JSON COMMENT 'Skills with proficiency levels',
    skills_normalized JSON COMMENT 'Normalized skill names',
    
    -- Description Tokens (CRITICAL for Models #3, #6, #7)
    description_tokens JSON COMMENT 'Word tokens',
    description_sentences JSON COMMENT 'Sentence segmentation',
    description_keywords JSON COMMENT 'Extracted keywords',
    description_key_phrases JSON COMMENT 'Key phrases',
    description_summary TEXT COMMENT 'Generated summary',
    description_sections JSON COMMENT 'Detected sections',
    
    -- Location Tokens
    location_city VARCHAR(100),
    location_province VARCHAR(100),
    location_normalized VARCHAR(255),
    location_is_remote BOOLEAN,
    
    -- Responsibility Tokens (for seniority detection)
    responsibilities_count INT,
    responsibilities_actions JSON COMMENT 'Extracted action verbs',
    responsibilities_categories JSON COMMENT 'Categorized responsibilities',
    responsibilities_seniority JSON COMMENT 'Seniority indicators',
    
    -- Qualification Tokens (CRITICAL for Model #4 salary prediction)
    qualifications_education VARCHAR(50),
    qualifications_experience_years INT,
    qualifications_certifications JSON,
    qualifications_required JSON,
    qualifications_preferred JSON,
    
    -- Benefit Tokens
    benefits_count INT,
    benefits_categories JSON,
    benefits_monetary JSON,
    benefits_has_insurance BOOLEAN,
    
    -- Processing Metadata
    processing_time_ms INT COMMENT 'Processing duration',
    tokenized_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_job_id (job_id),
    INDEX idx_level (title_level),
    INDEX idx_city (location_city),
    INDEX idx_education (qualifications_education),
    INDEX idx_experience (qualifications_experience_years),
    
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Detailed tokenization for ML training and NLP processing';


-- ============================================================================
-- LEVEL 3: Embeddings Table
-- Purpose: Vector embeddings for semantic search
-- Size: ~6 KB per job
-- Used by: Model #6 (similarity), Spaces #1, #4 (recommendations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS job_embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL UNIQUE,
    
    -- Embeddings (stored as JSON arrays)
    title_embedding JSON COMMENT '768-dim title embedding',
    description_embedding JSON COMMENT '768-dim description embedding',
    full_embedding JSON COMMENT '768-dim combined embedding',
    
    -- Model metadata
    embedding_model VARCHAR(100) DEFAULT 'bert-base-multilingual-cased',
    embedding_dim INT DEFAULT 768,
    embedding_version VARCHAR(50) COMMENT 'Model version for tracking',
    
    -- Performance metadata
    generation_time_ms INT COMMENT 'Embedding generation time',
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_job_id (job_id),
    INDEX idx_model (embedding_model),
    
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Vector embeddings for semantic search and recommendations';


-- ============================================================================
-- View: Combined Token Data (for easy querying)
-- ============================================================================

CREATE OR REPLACE VIEW job_tokens_complete AS
SELECT 
    j.id,
    j.judul,
    j.perusahaan,
    j.lokasi,
    
    -- Level 1 (Compact)
    JSON_EXTRACT(j.tokens, '$.title.level') as level_compact,
    JSON_EXTRACT(j.tokens, '$.skills.count') as skills_count,
    JSON_EXTRACT(j.tokens, '$.location.city') as city_compact,
    
    -- Level 2 (Detailed)
    d.title_level,
    d.title_role,
    d.skills_all,
    d.description_keywords,
    d.qualifications_experience_years,
    
    -- Level 3 (Embeddings)
    e.embedding_model,
    e.embedding_dim,
    
    -- Status
    j.is_tokenized,
    j.tokenized_at,
    d.tokenized_at as detailed_at,
    e.generated_at as embedded_at
    
FROM jobs j
LEFT JOIN job_tokens_detailed d ON j.id = d.job_id
LEFT JOIN job_embeddings e ON j.id = e.job_id;


-- ============================================================================
-- Usage Examples for Level 2:
-- ============================================================================

-- Get skills for ML training
-- SELECT job_id, skills_all, skills_categorized
-- FROM job_tokens_detailed
-- WHERE qualifications_experience_years >= 3;

-- Get description tokens for topic modeling
-- SELECT job_id, description_tokens, description_sentences
-- FROM job_tokens_detailed;

-- Find jobs with specific seniority indicators
-- SELECT j.judul, d.responsibilities_seniority
-- FROM jobs j
-- JOIN job_tokens_detailed d ON j.id = d.job_id
-- WHERE JSON_EXTRACT(d.responsibilities_seniority, '$.leadership') > 2;


-- ============================================================================
-- Usage Examples for Level 3:
-- ============================================================================

-- Get embeddings for similarity calculation
-- SELECT job_id, full_embedding
-- FROM job_embeddings
-- WHERE embedding_model = 'bert-base-multilingual-cased';

-- Check embedding coverage
-- SELECT 
--     COUNT(*) as total_jobs,
--     COUNT(e.id) as embedded_jobs,
--     ROUND(COUNT(e.id) * 100.0 / COUNT(*), 2) as coverage_pct
-- FROM jobs j
-- LEFT JOIN job_embeddings e ON j.id = e.job_id;


-- ============================================================================
-- Verify All Tables
-- ============================================================================

SHOW TABLES LIKE 'job_%';
DESCRIBE job_tokens_detailed;
DESCRIBE job_embeddings;
SELECT * FROM job_tokens_complete LIMIT 5;
