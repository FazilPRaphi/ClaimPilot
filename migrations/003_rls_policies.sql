/*
===============================================================================
Migration  : 003_rls_policies.sql
Project    : ClaimPilot
Author     : Fazil P Raphi

Description
-------------------------------------------------------------------------------
Enables Row Level Security and creates all database policies.

===============================================================================
*/
-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

ALTER TABLE claims ENABLE ROW LEVEL SECURITY;

ALTER TABLE claim_documents ENABLE ROW LEVEL SECURITY;

ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PROFILES POLICIES
-- ============================================================================

CREATE POLICY "Users can view their own profile"
ON profiles
FOR SELECT
USING (
    auth.uid() = id
);

CREATE POLICY "Users can update their own profile"
ON profiles
FOR UPDATE
USING (
    auth.uid() = id
);

CREATE POLICY "Users can insert their own profile"
ON profiles
FOR INSERT
WITH CHECK (
    auth.uid() = id
);

-- ============================================================================
-- CLAIMS POLICIES
-- ============================================================================

CREATE POLICY "Users can manage their own claims"
ON claims
FOR ALL
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- ============================================================================
-- CLAIM DOCUMENTS POLICIES
-- ============================================================================

CREATE POLICY "Users can manage documents for their own claims"
ON claim_documents
FOR ALL
USING (
    EXISTS (
        SELECT 1
        FROM claims
        WHERE claims.id = claim_documents.claim_id
        AND claims.user_id = auth.uid()
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM claims
        WHERE claims.id = claim_documents.claim_id
        AND claims.user_id = auth.uid()
    )
);

-- ============================================================================
-- AGENT RUNS POLICIES
-- ============================================================================

CREATE POLICY "Users can view agent runs for their own claims"
ON agent_runs
FOR SELECT
USING (
    EXISTS (
        SELECT 1
        FROM claims
        WHERE claims.id = agent_runs.claim_id
        AND claims.user_id = auth.uid()
    )
);

-- ============================================================================
-- AUDIT LOGS POLICIES
-- ============================================================================

CREATE POLICY "Users can view their own audit logs"
ON audit_logs
FOR SELECT
USING (
    auth.uid() = user_id
);

-- ============================================================================
-- STORAGE POLICIES
-- Bucket: claim-files
-- ============================================================================

CREATE POLICY "Users can upload their own claim files"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'claim-files'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can view their own claim files"
ON storage.objects
FOR SELECT
TO authenticated
USING (
    bucket_id = 'claim-files'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete their own claim files"
ON storage.objects
FOR DELETE
TO authenticated
USING (
    bucket_id = 'claim-files'
    AND auth.uid()::text = (storage.foldername(name))[1]
);