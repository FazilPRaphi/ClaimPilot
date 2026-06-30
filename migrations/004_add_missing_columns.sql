/*
===============================================================================
Migration  : 004_add_missing_columns.sql
Project    : ClaimPilot

Description
-------------------------------------------------------------------------------
Adds columns that exist in application code but were absent from the initial
schema migration, causing INSERT/UPDATE failures:

  claims table:
    - structured_data   JSONB   (AI-extracted structured claim fields)
    - ai_processed_at   TIMESTAMPTZ  (timestamp of last AI analysis)

  claim_documents table:
    - ocr_confidence    REAL    (average OCR confidence 0.0 – 100.0)

Run this migration in Supabase SQL editor or via psql before starting the app.
===============================================================================
*/

-- ============================================================================
-- claims: add AI analysis columns
-- ============================================================================

ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS structured_data   JSONB,
    ADD COLUMN IF NOT EXISTS ai_processed_at   TIMESTAMPTZ;

-- ============================================================================
-- claim_documents: add OCR confidence column
-- ============================================================================

ALTER TABLE claim_documents
    ADD COLUMN IF NOT EXISTS ocr_confidence REAL;

COMMIT;
