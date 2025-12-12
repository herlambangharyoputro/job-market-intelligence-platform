-- ============================================================================
-- Phase 4: Tokenization Storage - Level 1 (Compact JSON)
-- Purpose: Fast analytics, dashboards, HF Dataset #2, #5
-- Size: ~500 bytes per job
-- ============================================================================

USE job_market_intelligence_platform;

-- Add columns to jobs table
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS tokens JSON COMMENT 'Compact tokenization results for analytics',
ADD COLUMN IF NOT EXISTS is_tokenized BOOLEAN DEFAULT FALSE COMMENT 'Whether job has been tokenized',
ADD COLUMN IF NOT EXISTS tokenized_at DATETIME COMMENT 'When tokenization was completed';

-- Add indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_is_tokenized ON jobs(is_tokenized);
CREATE INDEX IF NOT EXISTS idx_tokenized_at ON jobs(tokenized_at);

-- JSON indexes for common queries (MySQL 8.0+)
-- These enable fast filtering on JSON fields
ALTER TABLE jobs ADD INDEX idx_tokens_level ((CAST(JSON_EXTRACT(tokens, '$.title.level') AS CHAR(50))));
ALTER TABLE jobs ADD INDEX idx_tokens_city ((CAST(JSON_EXTRACT(tokens, '$.location.city') AS CHAR(100))));

-- Verify structure
DESCRIBE jobs;

-- ============================================================================
-- Usage Examples:
-- ============================================================================

-- Query by level
-- SELECT id, judul FROM jobs 
-- WHERE JSON_EXTRACT(tokens, '$.title.level') = 'senior';

-- Query by skills
-- SELECT id, judul FROM jobs 
-- WHERE JSON_CONTAINS(JSON_EXTRACT(tokens, '$.skills.top'), '"python"');

-- Query remote jobs
-- SELECT id, judul FROM jobs 
-- WHERE JSON_EXTRACT(tokens, '$.location.remote') = true;

-- Get completeness stats
-- SELECT 
--     AVG(JSON_EXTRACT(tokens, '$.stats.completeness')) as avg_completeness,
--     COUNT(*) as tokenized_count
-- FROM jobs
-- WHERE is_tokenized = TRUE;

-- ============================================================================
-- Rollback (if needed):
-- ============================================================================

-- ALTER TABLE jobs 
-- DROP COLUMN tokens,
-- DROP COLUMN is_tokenized,
-- DROP COLUMN tokenized_at;
