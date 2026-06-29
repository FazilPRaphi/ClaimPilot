/*
===============================================================================
Migration  : 001_initial_schema.sql
Project    : ClaimPilot
Author     : Fazil P Raphi
Version    : 1.0.0

Description
-------------------------------------------------------------------------------
Initial database schema.

This migration creates:

• PostgreSQL extensions
• Custom enums
• Utility trigger functions
• Core business tables
• Foreign keys
• Indexes
• Automatic updated_at triggers

NOTE

Do NOT edit this migration after it has been executed.

Future changes must be created as new migrations.

===============================================================================
*/

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================================
-- USER ROLE
-- ============================================================================

CREATE TYPE user_role AS ENUM (
    'user',
    'admin'
);

-- ============================================================================
-- CLAIM STATUS
-- ============================================================================

CREATE TYPE claim_status AS ENUM (
    'draft',
    'uploaded',
    'processing',
    'analysis_complete',
    'ready',
    'completed',
    'failed'
);

-- ============================================================================
-- CLAIM STAGE
-- ============================================================================

CREATE TYPE claim_stage AS ENUM (
    'upload',
    'ocr',
    'intake',
    'policy_analysis',
    'evidence_validation',
    'scoring',
    'submission',
    'completed'
);

-- ============================================================================
-- DOCUMENT TYPE
-- ============================================================================

CREATE TYPE document_type AS ENUM (
    'receipt',
    'invoice',
    'policy',
    'damage_photo',
    'supporting_document',
    'other'
);

-- ============================================================================
-- DOCUMENT STATUS
-- ============================================================================

CREATE TYPE document_status AS ENUM (
    'uploaded',
    'processing',
    'processed',
    'failed'
);

-- ============================================================================
-- AGENT STATUS
-- ============================================================================

CREATE TYPE agent_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed'
);
-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


-- ============================================================================
-- TABLE: profiles
-- Extends Supabase auth.users with application-specific information.
-- ============================================================================

CREATE TABLE profiles (

    id UUID PRIMARY KEY
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    full_name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    avatar_url TEXT,

    role user_role NOT NULL
        DEFAULT 'user',

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    deleted_at TIMESTAMPTZ

);

-- ============================================================================
-- TRIGGER: profiles_updated_at
-- ============================================================================

CREATE TRIGGER profiles_updated_at
BEFORE UPDATE
ON profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- TABLE: claims
-- Stores insurance/warranty claims submitted by users.
-- ============================================================================

CREATE TABLE claims (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    claim_number TEXT NOT NULL UNIQUE,

    user_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    title TEXT NOT NULL,

    description TEXT,

    claim_type TEXT NOT NULL,

    status claim_status NOT NULL
        DEFAULT 'draft',

    current_stage claim_stage NOT NULL
        DEFAULT 'upload',

    readiness_score SMALLINT
        DEFAULT 0
        CHECK (readiness_score BETWEEN 0 AND 100),

    confidence_score SMALLINT
        DEFAULT 0
        CHECK (confidence_score BETWEEN 0 AND 100),

    ai_summary TEXT,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    deleted_at TIMESTAMPTZ

);

-- ============================================================================
-- TRIGGER: claims_updated_at
-- ============================================================================

CREATE TRIGGER claims_updated_at
BEFORE UPDATE
ON claims
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INDEXES: claims
-- ============================================================================

CREATE INDEX idx_claims_user_id
ON claims(user_id);

CREATE INDEX idx_claims_status
ON claims(status);

CREATE INDEX idx_claims_stage
ON claims(current_stage);

CREATE INDEX idx_claims_deleted_at
ON claims(deleted_at);

CREATE INDEX idx_claims_created_at
ON claims(created_at DESC);


-- ============================================================================
-- TABLE: claim_documents
-- Stores all documents uploaded for a claim.
-- ============================================================================

CREATE TABLE claim_documents (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    claim_id UUID NOT NULL
        REFERENCES claims(id)
        ON DELETE CASCADE,

    file_name TEXT NOT NULL,

    storage_path TEXT NOT NULL,

    document_type document_type NOT NULL,

    extracted_text TEXT,

    upload_status document_status NOT NULL
        DEFAULT 'uploaded',

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    deleted_at TIMESTAMPTZ

);

-- ============================================================================
-- TRIGGER: claim_documents_updated_at
-- ============================================================================

CREATE TRIGGER claim_documents_updated_at
BEFORE UPDATE
ON claim_documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INDEXES: claim_documents
-- ============================================================================

CREATE INDEX idx_claim_documents_claim_id
ON claim_documents(claim_id);

CREATE INDEX idx_claim_documents_type
ON claim_documents(document_type);

CREATE INDEX idx_claim_documents_status
ON claim_documents(upload_status);

CREATE INDEX idx_claim_documents_deleted_at
ON claim_documents(deleted_at);

-- ============================================================================
-- TABLE: agent_runs
-- Logs every AI agent execution for a claim.
-- ============================================================================

CREATE TABLE agent_runs (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    claim_id UUID NOT NULL
        REFERENCES claims(id)
        ON DELETE CASCADE,

    agent_name TEXT NOT NULL,

    status agent_status NOT NULL
        DEFAULT 'pending',

    started_at TIMESTAMPTZ,

    finished_at TIMESTAMPTZ,

    duration_ms INTEGER,

    input_tokens INTEGER,

    output_tokens INTEGER,

    result JSONB,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    deleted_at TIMESTAMPTZ

);

-- ============================================================================
-- TRIGGER: agent_runs_updated_at
-- ============================================================================

CREATE TRIGGER agent_runs_updated_at
BEFORE UPDATE
ON agent_runs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INDEXES: agent_runs
-- ============================================================================

CREATE INDEX idx_agent_runs_claim_id
ON agent_runs(claim_id);

CREATE INDEX idx_agent_runs_status
ON agent_runs(status);

CREATE INDEX idx_agent_runs_created_at
ON agent_runs(created_at DESC);

CREATE INDEX idx_agent_runs_deleted_at
ON agent_runs(deleted_at);

-- ============================================================================
-- TABLE: audit_logs
-- Stores important user and system actions.
-- ============================================================================

CREATE TABLE audit_logs (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES profiles(id)
        ON DELETE SET NULL,

    claim_id UUID
        REFERENCES claims(id)
        ON DELETE SET NULL,

    action TEXT NOT NULL,

    details JSONB,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    deleted_at TIMESTAMPTZ

);

-- ============================================================================
-- TRIGGER: audit_logs_updated_at
-- ============================================================================

CREATE TRIGGER audit_logs_updated_at
BEFORE UPDATE
ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INDEXES: audit_logs
-- ============================================================================

CREATE INDEX idx_audit_logs_user_id
ON audit_logs(user_id);

CREATE INDEX idx_audit_logs_claim_id
ON audit_logs(claim_id);

CREATE INDEX idx_audit_logs_action
ON audit_logs(action);

CREATE INDEX idx_audit_logs_created_at
ON audit_logs(created_at DESC);

CREATE INDEX idx_audit_logs_deleted_at
ON audit_logs(deleted_at);

COMMIT;